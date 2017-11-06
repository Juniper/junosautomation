# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.

from jnpr.junos import Device                    # (1)
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
import argparse
from time import sleep

arguments = {                                    # (2)
    "interface": "Name of the interface to disable/enable",
    "delay": "Time to wait before enabling the interface (seconds)",
}

def config_xml(interface_name, disable_attributes):      # (3)
    return """
        <configuration>
            <interfaces>
                <interface>
                    <name>{0}</name>
                    <disable {1}/>
                </interface>
            </interfaces>
        </configuration>
    """.format(interface_name, disable_attributes)

def change_config(dev_cfg, delta_config, log_message):       # (4)
    print "%s: Locking the configuration" % log_message
    try:
        dev_cfg.lock()
    except LockError:
        print "Error: Unable to lock configuration"
        return False

    print "%s: Loading configuration changes" % log_message
    try:
        dev_cfg.load(delta_config, format="xml", merge=True)
    except ConfigLoadError as err:
        print "Unable to load configuration changes: \n" + err
        print "Unlocking the configuration"
        try:
            dev_cfg.unlock()
        except UnlockError:
            print "Error: Unable to unlock configuration"
        return False
   
    print "%s: Committing the configuration" % log_message
    try:
        dev_cfg.commit()
    except CommitError:
        print "Error: Unable to commit configuration"
        print "Unlocking the configuration"
        try:
            dev_cfg.unlock()
        except UnlockError:
            print "Error: Unable to unlock configuration"
        return False
   
    print "%s: Unlocking the configuration" % log_message
    try:
        dev_cfg.unlock()
    except UnlockError:
        print "Error: Unable to unlock configuration"
        return False

    return True

def main():                                      # (5)
    parser = argparse.ArgumentParser()           # (6) 
    for key in arguments:
        parser.add_argument(('-' + key), required=True, help=arguments[key])
    args = parser.parse_args()

    with Device() as dev:                        # (7)
        dev.bind( cu=Config )                    # (8) 
        if change_config(dev.cu, config_xml(args.interface, ""),     # (9)
                "Disabling interface"):
            print "Waiting %s seconds..." % args.delay
            sleep(float(args.delay))                              # (10)
            if change_config(dev.cu, config_xml(args.interface, "delete='delete'"), 
                    "Enabling interface"):                        # (11)
                print "Interface bounce script finished successfully."
            else:
                print "Error enabling the interface, it will remain disabled."
    
if __name__ == "__main__":                                        # (12) 
    main()
