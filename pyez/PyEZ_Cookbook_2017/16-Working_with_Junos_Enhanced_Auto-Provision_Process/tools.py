# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.
import re
import os
import time
import json
import yaml
import jinja2
import pprint
import hashlib
import logging
from pprint import pprint
from jnpr.junos import Device
from jnpr.junos import exception
from jnpr.junos.utils.sw import SW




__author__ = 'juniper'

def install_progress(dev, msg):
        print("{}:{}".format(dev.hostname, msg))

def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096),b""):
            hash.update(chunk)
    return hash.hexdigest()


class Tools:
    """
    Collection of tools that will be used
    for Jeap 2.0
    """

    __url = 'http://kb.juniper.net/InfoCenter/index?page=content&id=KB21476'
    __known_hosts = []
    __new_hosts = []
    __counter_for_lease_read = 0
    __interval_for_lease_read = 6
    customer_requirements = []      #list of dictionaries


    def __init__(self):
        self.customer_requirements = self.read_customer_requirements('Data/CustomerRequirement.json')

    def read_customer_requirements(self, path):
        complete_path = os.path.join(os.getcwd(), path)
        with open(complete_path, 'r') as reqFile:
            data = json.load(reqFile)
            #print data ["Products"]
            return data["Products"]


    def lease_read(self, path):
        """
        Initial read from 'dhcpd.leases' file
        Get {ip, mac}
        """

        map_from_lease = []
        concise_map_from_lease = []
        tmp_lib = set()
        # this include address from 0.0.0.0 - 255.255.255.255
        pattern_for_ip = r"(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)"
        pattern_for_mac = r"(?:(?:[0-9a-f][0-9a-f]:){5}(?:[0-9a-f][0-9a-f]))"

        # read leases file, abstract IP and Mac in order
        with open(path, 'r') as leases_file:
            content = leases_file.read()
            tmp_hosts = re.findall(pattern_for_ip, content)
            tmp_mac = re.findall(pattern_for_mac, content)

        # match IP and Mac
        for i in range(0, len(tmp_hosts)):
            tmp = {"ip": tmp_hosts[i], "mac": tmp_mac[i]}
            map_from_lease.append(tmp)
        # remove duplicates
        for cell in map_from_lease:
            t = tuple(cell.items())
            if t not in tmp_lib:
                tmp_lib.add(t)
                concise_map_from_lease.append(cell)

        if concise_map_from_lease:
            print("\nHosts read from lease file (inside tools):")
            pprint(concise_map_from_lease)

        return concise_map_from_lease

    def mac_compare(self, sample_mac, target_mac):
        """
        For SRX, bootp ge-0/0/0 => ge-0/0/0.mac = chassis.mac
        For  EX, bootp ge-0/0/0 => vlan.mac = chassis.mac + 1
        """
        sample_mac_int = int(sample_mac.replace(':', ''), 16)
        target_mac_int = int(target_mac.replace(':', ''), 16)
        if sample_mac_int == target_mac_int or sample_mac_int == (target_mac_int + 1):
            return True
        else:
            return False

    def mac_return(self, model, chassis_mac):
        """
        Since SRX and EX has different processure of autoinstall,
        the mac they are using is not always Chassis Mac
        Branch SRX:
        (physical) ge-0/0/0 -> (virtual) ge-0/0/0 = (hardware addr.) chassis mac
        EX:
        (physical) ge-0/0/0 -> (virtual) vlan = (hardware addr.)chassis mac + 1
        aim to return proper mac address to compare with mac from dhcp server record
        """
        if "SRX" in model:
            return chassis_mac
        elif "EX" in model:
            target_mac_hex = hex(int(chassis_mac.replace(':', ''), 16) + 1)[2:]
            target_mac_str = ':'.join([target_mac_hex[i:i+2] for i in range(0, len(target_mac_hex), 2)])
            return target_mac_str

    def device_conn(self, host_ip):
        user = "username"
        password = "password"
        return Device(host=host_ip, user=user, password=password, port="22")

    def print_base_info(self, device):
        print (str(device.facts["model"]) + ":   " + str(device.facts["version"]) + "\n")

    def config_composer(self, model, hostname, junos_on_box_version):
        """
         Using Yaml and Jinja2 generate dynamic templates
        """
        if ("SRX3" in model) or ("vsrx" in model):
            template_filename = "SRX_template.j2"
            network_parameter_filename = "SRX_networkParameters.yaml"
        elif "EX" in model:
            template_filename = "EX_template.j2"
            network_parameter_filename = "EX_networkParameters.yaml"
        complete_path = os.path.join(os.getcwd(), 'Config')
        ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(complete_path))
        template = ENV.get_template(template_filename)
        with open(complete_path + "/" + network_parameter_filename) as yamlfile:
            dict = yaml.load(yamlfile)  # yaml file is loaded as a dictionary with key value pairs
        addition = {"hostname": hostname, "version": junos_on_box_version}
        dict.update(addition)
        # print dict
        content = template.render(dict)
        # print content
        target = open("Config_History/" + hostname + ".set", 'w')
        target.write(content)
        target.close()

    def junos_image_filename_builder(self, model, junos):
        if "EX" in model:
            match = re.match(r"([a-z]+)([0-9]+)", model, re.I)
            necessary_filename = "jinstall-ex-" + match.groups()[1] + "-" + str(junos)
        elif "SRX" in model:
            necessary_filename = "junos-srxsme-" + str(junos)
        return necessary_filename;


    def local_junos_dir_check(self, sample_model, target_version):
        """ read file names under local stored junos,
            extract label and compare them with targeted junos version
            return local filename if we have;
            return False if we don't
        """
        part_filename = self.junos_image_filename_builder(sample_model, target_version)
        print("Local junos directory check for version " + target_version + " ...")
        for filename in os.listdir("Junos/"):
            if filename.endswith(".tgz") and (part_filename in filename):
                print("Found proper image ...")
                return filename
        # if doesn't find, return False
        return False



    def junos_auto_install(self,host_ip, path, device):
        """
        Call PyEz to secure install new junos version
        to remote srx host
        """

        sw = SW(device)
        path = os.path.join(os.getcwd(),path)
        print path,type(path)
        try:
            ok = sw.install(package=path, progress=install_progress)
        except Exception as err:
            print("Install error")
            raise err
        if ok is True:
            print("\nSoftware installation succeeded")
        else:
            print(ok)
            time.sleep(30)
        try:
            rsp = sw.reboot()
            print(rsp)
        except exception.ConnectClosedError:
            print("About to loose connection ..")
        finally:
            print("Please wait for the box to wake-up!")
            time.sleep(120)
            dev = self.device_conn(host_ip)
            feeds = dev.probe(10)
            while not feeds:
                feeds = dev.probe(20)
                #print("probing in 20 seconds interval")
            print("\n\nConnecting to box now ...")
            dev.open()
            print("Connected")
            print("New version:")
            self.print_base_info(dev)
            return dev

    def junos_version_serial_analyze(self, sample):
        holder = 0
        result = []
        counter = 0
        for x in sample:
            counter += 1
            if x.isdigit():
                holder = holder * 10 + int(x)
                if counter == len(sample):
                    result.append(holder)
            else:
                if holder != 0:
                    result.append(holder)
                    holder = 0
                if x.isalpha():
                    result.append(str(x))
                else:
                    continue
        return result

    def junos_version_compare(self, sample_version, target_version):
        sample_series = self.junos_version_serial_analyze(sample_version)
        target_series = self.junos_version_serial_analyze(target_version)
        print sample_series
        print target_series
        count = min(len(sample_series), len(target_series))
        #print("inside junos_version_compare: count "+ str(count))

        for x in range(count):
            if sample_series[x] != target_series[x]:
                if sample_series[x] > target_series[x]:
                    # print("current one has newer version @" + str(x+1) + " digit")
                    return 1
                elif sample_series[x] < target_series[x]:
                    # print("current one has older version")
                    return -1
        # if compare every digit and they are the same till the end
        # it indicates that they are the same
        # just of different length
        return 0

# t = Tools()
