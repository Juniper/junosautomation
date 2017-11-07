# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.
#!/usr/bin/python3

from jnpr.junos import Device                              # (1)
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
import jinja2
import os
import yaml

USER = "lab"                                               # (2)
PASSWD = "lab123"

def render(full_filename, context):                        # (3)
    path, filename = os.path.split(full_filename)
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')).get_template(filename)
    return template.render(context)

def main():                                                # (4)
    with open("l3vpn-data.yaml") as var_file:
        l3vpn_data = yaml.load(var_file)

    for PE in l3vpn_data["PEs"]:                                # (5)
        print("Working on device %s" % PE)
        vars = l3vpn_data["PEs"][PE].copy()                     # (6)
        vars.update({"customers": l3vpn_data["customers"]})
        result_conf = render("l3vpn_config.jinja2", vars)       # (7)

        try:                                                    # (8)
            with Device(host=l3vpn_data["PEs"][PE]["management_ip"],
                        user=USER, password=PASSWD) as dev:
                # open and close is done automatically by context manager
                with Config(dev, mode="exclusive") as conf:
                    # exclusive locks are treated automatically by context manager
                    conf.load(result_conf, format="text")
                    diff = conf.diff()                          # (9)
                    if diff is None:
                        print("Configuration is up to date.")
                    else:
                        print("Config diff to be committed on device:")
                        print(diff)
                        conf.commit()                           # (10)
        except LockError:
            print("\nError applying config: configuration was locked!")
        except ConnectRefusedError:
            print("\nError: Device connection refused!")
        except ConnectTimeoutError:
            print("\nError: Device connection timed out!")
        except ConnectAuthError:
            print("\nError: Authentication failure!")
        except ConfigLoadError as ex:
            print("\nError: " + str(ex))
        else:                                                   # (11)
            if diff is not None:
                print("Config committed successfully!")

if __name__ == "__main__":                                      # (12)
    main()
