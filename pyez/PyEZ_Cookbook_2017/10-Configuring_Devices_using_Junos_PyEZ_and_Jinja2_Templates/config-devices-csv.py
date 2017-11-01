#!/usr/bin/env python3
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import csv

USER = "admin"
PW = "starwars"
CONFIG_FILE = "config.txt"

def config_multi_devices(csv_file='config-data.csv'):
    with open(csv_file) as f:
        csvfile = csv.DictReader(f)

        for row in csvfile:
            firewall = row['firewall']
            values = {
                'dns_server': row['dns_server'],
                'ntp_server': row['ntp_server'],
                'snmp_location': row['snmp_location'],
                'snmp_contact': row['snmp_contact'],
                'snmp_community': row['snmp_community'],
                'snmp_trap_recvr': row['snmp_trap_recvr']
            }

            dev = Device(host=firewall, user=USER, password=PW).open()
            with Config(dev) as cu:
                cu.load(template_path=CONFIG_FILE, template_vars=values, format='set', merge=True)
                cu.commit(timeout=30)
                print("Committing the configuration on device: {}".format(firewall))
            dev.close()

if __name__ == "__main__":
    config_multi_devices()