# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.
#!/usr/bin/env python

import time
import logging
from tools import Tools
from jnpr.junos import exception
from jnpr.junos.utils.config import Config


__author__ = 'juniper'

if __name__ == "__main__":
    """
    Aim to do simple logic here
    And call modules to do specific function
    """
    tools = Tools()

    known_hosts = []        # hosts finished provisioning
    new_hosts = []          # hosts to-be provisioned
    tmp_hosts = []          # hosts read from leases file
    box_to_configure = tools.customer_requirements      # library for customer required to-be provisioned boxes


    # an always running loop here to read
    while True:
        try:
            # tmp_hosts: list of dictionaries with ip and mac
            tmp_hosts = tools.lease_read("/var/lib/dhcp/dhcpd.leases")
	    if not tmp_hosts:
                print("don't have any DHCP client now, please wait.")
                time.sleep(15)
            else:
                break
        except IOError:
            print("Please restart your dhcp service, dhcpd.leases file have been removed somehow")
            time.sleep(30)

    while True:
        for tester in tmp_hosts:
            # first filter by list of seen hosts in the past
            if tester not in known_hosts:
                # then filter by MAC from customer document
                for item in box_to_configure:
                    if tools.mac_compare(tester["mac"], item["mac"]):
                        # merge two info source together
                        # thus don't need to lookup IP every time
                        item["ip"] = tester["ip"]
                        new_hosts.append(item)
                        break

        if not new_hosts:
            print("\nDon't have any new host come online")
        else:
            print("\nBelow are new hosts from lease file:")
            print(new_hosts)

        while new_hosts:
            # call another function to do that
            sample = new_hosts.pop(0)
            print("\nTarget hosts:\n\t" + str(sample["model"]) + " @ " + str(sample["ip"]))
            # reach out to srx
            dev = tools.device_conn(sample["ip"])
            cu = Config(dev)
            print("Connecting ...")
            try:
                dev.open()
                print("Connected")
            except exception.ConnectAuthError:
                print("Username and password doesn't match")
                print("Please double check your credentials and try again later.")
                continue
            except exception.ConnectTimeoutError:
                print("Connection timeout, will try again later")
                continue
            except:
                print("Cannot reach out to the device now, will try again later")
                continue

            # pull info from box current settings
            sample_on_box_model = dev.facts["model"]
            if sample_on_box_model != sample["model"]:
                print ("\nWarning: model doesn't match!\n")
            sample_on_box_version = dev.facts["version"]
            if sample_on_box_model == "vSRX":
                print("Sorry, we don't support vSRX right now")
                known_hosts.append(sample)
                continue
            print("\nCurrent Config:")
            print("\t" + sample_on_box_model + ":  " + sample_on_box_version)

            # version check
            feedback = tools.junos_version_compare(sample_on_box_version, sample["junos"])
            print feedback
            if feedback >= 0:
                print("On-box Junos version at " + sample["ip"] + "(" + sample_on_box_model + ")" + "is NOT OLDER than customer required")
                print("No need to upgrade\n")
            else:
                print("On-box Junos version at " + sample["ip"] + "(" + sample_on_box_model + ")" + "is OLDER than customer required")
                print("Need to upgrade\n")
                # otherwise we have to upgrade
                # first check if we store that junos file locally
                filename = tools.local_junos_dir_check(sample["model"], sample["junos"])
                if filename:
                    # after have file locally, call PyEz to install that
                    dev = tools.junos_auto_install(str(sample["ip"]), "Junos/" + filename, dev)
                else:
                    # if we don't have file locally, print out warning
                    print("Failed to find customer required image locally, please download in Junos folder before we can perform system upgrade")
                    # log it here
                    logging.info("Need to download junos " + sample["junos"] + "for " + sample["model"])
                    ##constructure here need to optimize
            cu = Config(dev)
            print("\n\nPushing down another configuration file now ")
            tools.config_composer(sample["model"], sample["hostname"], sample_on_box_version)
            cu.load(path="Config_History/" + sample["hostname"] + ".set")
            try:
                cu.commit(timeout=180)
            except exception.RpcTimeoutError:
                print("Need longer time to commit, please adjust commit timeout value ...")
                time.sleep(5)
            print("Configuration Updated")
            tmp = {}
            tmp["ip"] = sample["ip"]
            tmp ["mac"]= tools.mac_return(sample["model"], str(sample["mac"]))
            known_hosts.append(tmp)
            dev.close()

            print("Remaining hosts to configure this round:")
            print(new_hosts)         # empty list

        print("\nRead leases file again:")
        tmp_hosts = tools.lease_read("/var/lib/dhcp/dhcpd.leases")
        time.sleep(10)
        #break
        #print("Clear know_hosts list for test purpose:")
        #known_hosts = []
