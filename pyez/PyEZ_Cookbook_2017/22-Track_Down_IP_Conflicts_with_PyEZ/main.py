# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved

'''
Identify physical switch interfaces associated within an IP conflict.

This program finds IP conflicts within a JUNOS based L3/L3 tiered network, and tracks down which access
interfaces the MAC addresses are coming from.

Copyright (c) 2017 Matthew Mellin

This library is free software.  It is licensed under the Apache License version 2.0.


The manuf.py library is copyright (c) 2017 Michael Huang and licensed under the terms of the GNU Lesser General Public
License version 3.0 (or any later version) and the Apache License version 2.0. <https://github.com/coolbho3k/manuf>

For more information, see:

<http://www.gnu.org/licenses/>
<http://www.apache.org/licenses/>

'''
import argparse
import getpass
import json
import os
import socket
import sys
from pathlib import Path
from collections import defaultdict
from pkgs.utils.log import get_logger
from pkgs.utils import ipconflictslib as ipc


logger = get_logger(__name__)


def create_help():
    """ Build help documentation and creates program arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument("seed_router", type=str,
                        help="Gateway router for hosts to begin search.  Hostname or IP.")
    parser.add_argument("-u", "--user", type=str, help="Seed_router username for login.")
    # parser.add_argument("-p", "--password", type=str, help="Seed_router login password.")
    parser.add_argument("-m", "--mode", type=str, default="password",
                        help="Method of login: 'ssh-key' or 'password'. Defaults to password.")
    parser.add_argument("-f", "--file", type=str, default="duplicate_ips",
                        help="Name of duplicate IP log file on router.")
    parser.add_argument("--connect_timeout", type=int, help="PyEz device connect timeout")
    parser.add_argument("--processes", type=int, help="Max number of threads to run concurrent.")
    parser.add_argument("--vendor", action='store_true', help="Try to resolve the HW vendor for each MAC.")
    parser.add_argument("--update_vendor", action='store_true',
                        help="Update local copy of Wireshark's OUI DB from the web.")
    parser.add_argument("--router_log_path", type=str, default='/var/log/',
                        help="Folder path on router where the 'duplicate_ips' log is stored. Defaults to 'var/log/")
    args = parser.parse_args()

    return args


def main():
    # Script Arguments
    args = create_help()
    seed_router = args.seed_router
    username = args.user
    password = None
    auth_mode = args.mode
    dup_filename = args.file
    router_log_path = args.router_log_path
    local_log_dir = "logs/"
    connect_timeout = args.connect_timeout
    resolve_vendor = args.vendor
    update_vendor = args.update_vendor
    processes = args.processes

    if auth_mode == 'password':
        password = getpass.getpass()

    # Initialize variables
    credentials = {'username': username, 'password': password, 'auth_mode': auth_mode}
    base_dir = os.path.dirname(os.path.realpath(__file__))
    local_log_abspath = os.path.join(base_dir, local_log_dir)
    data_dir_abspath = os.path.join(base_dir, 'data')
    vlan_id_name_dict = {}
    vlans = defaultdict(list)
    remote_systems = defaultdict(dict)
    seed_ip = socket.gethostbyname(seed_router)
    manuf_file_path = Path(os.path.join(data_dir_abspath, "manuf"))
    updated = False

    # Attempt to update the Wireshark OUI directory if vendor resolution is required.
    if resolve_vendor:
        # Verify that a Wireshark OUI file exists
        if not manuf_file_path.is_file():
            logger.info("OUI resolution file does not exist.")
            logger.info("Downloading and updating '{}' Wireshark OUI file.".format(manuf_file_path.as_posix()))
            try:
                ipc.update_vendor_file(path=manuf_file_path)
                logger.info("Download successful.")
                updated = True
            except Exception as e:
                logger.error(e)
                logger.error("Download failed. MAC resolution disabled.")
                resolve_vendor = False

    # Attempt to update the OUI file if it hasn't been already.
    if update_vendor:
        # If we've already updated, skip updating again.
        if updated:
            pass
        else:
            logger.info("Downloading and updating '{}' Wireshark OUI file.".format(manuf_file_path.as_posix()))
            try:
                ipc.update_vendor_file(path=manuf_file_path)
                logger.info("Download successful.")
                updated = True
            except URLError as e:
                logger.error("Download failed.")

    # Begin print log output header
    logger.info("#" * 60)
    logger.info("Locating Duplicate IPs in your Network")
    logger.info("#" * 60)
    logger.info('\n')
    logger.info("Opening a connection to the Gateway Router.\n")

    # Begin connecting to network and finding baseline information
    with ipc.connect_dut(seed_router, credentials, connect_timeout=connect_timeout) as dev:
        personality = dev.facts.get('personality')
        model = dev.facts.get('model')
        name = dev.facts.get('hostname')
        description = model + " " + dev.facts.get('serialnumber')
        remote_systems[seed_ip] = {'facts': {'personality': personality, 'model': model}, 'name': name,
                                   'description': description, 'searched': False}

        """ Step 1 - Parse the log file and identify Potential Duplicate IPs """
        logfile = ipc.LogFile(dup_filename, local_log_abspath, router_log_path)
        logger.info('Copying log file {} to local disk...'.format(logfile.filename))

        seed_dict = logfile.create_seed_dict(dev)

        logger.debug("{} -> {}".format(logfile.remote_file_path, logfile.local_file_path))
        logger.debug("Creating the 'seed_dict' data structure for parsing.")
        logger.info("Log file copied, starting to parse...")
        logger.debug(json.dumps(seed_dict, indent=2))
        logger.info("Log file parsed.  Starting to find mappings for IP, Vlan and MAC.")

        # Validate that you have any potential duplicate IP logs, else exit.
        for item in seed_dict.values():
            if len(item) == 0:
                logger.info("No duplicate IP entries found in the provided Duplicate IP log.  Exiting.")
                sys.exit(1)

        """ Step 2 - Determine which VLANs and interfaces the IPs were learned over """
        iter1 = ipc.determine_vlan(dev, seed_dict)
        for data_tuple in iter1:
            vlan_name = data_tuple[0]
            vlan_id = data_tuple[1]
            ip = data_tuple[2]
            macs = data_tuple[3]
            logger.info("Potential duplicate IP {} found on Vlan {}({})".format(ip, vlan_name, vlan_id))
            vlan_id_name_dict[vlan_id] = vlan_name
            vlans[vlan_id].extend([mac for mac in macs if mac not in vlans[vlan_id]])

        remote_systems[seed_ip]['vlans'] = vlans
        logger.debug(vlan_id_name_dict)

    logger.info("Begin to scan the systems found attached to the Seed Router.\n")
    scanned_systems, all_macs_found = ipc.system_scan(remote_systems, credentials, processes,
                                                      connect_timeout=connect_timeout)
    logger.debug(json.dumps(scanned_systems, indent=2))
    logger.info("Search complete.")

    output = ipc.create_output_structures(scanned_systems, seed_dict, resolve_vendor=resolve_vendor)
    logger.debug(json.dumps(output, indent=2))

    print("\n\n")
    logger.info("FINAL OUTPUT: \n")
    for vlan_id, ip_values in output.items():
        vlan_name = vlan_id_name_dict[vlan_id]
        logger.info("Vlan {}: {}".format(vlan_name, vlan_id))
        for ip, tuples in ip_values.items():
            logger.info("\tIP {} found on:".format(ip))
            for data in tuples:
                mac = data[0]
                vendor = data[1]
                name = data[2]
                mgt_ip = data[3]
                if not mgt_ip:
                    if not vendor:
                        logger.info("\t\t{} -> {} (MAC not found in search) ".format(mac, 'System name not found'))
                    else:
                        logger.info("\t\t{}({}) -> {} (MAC not found in search) ".format(mac, vendor,
                                                                                         'System name not found'))
                else:
                    interface = data[4]
                    if not vendor:
                        logger.info("\t\t{} -> {}: {} (mgt IP: {})".format(mac, name, interface, mgt_ip))
                    else:
                        logger.info("\t\t{}({}) -> {}: {} (mgt IP: {})".format(mac, vendor, name, interface, mgt_ip))


if __name__ == '__main__':
    main()
