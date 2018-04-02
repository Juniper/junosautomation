#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Example op script
# Uses table/view to gather info about logged in users

import argparse
import yaml

from jnpr.junos.factory.factory_loader import FactoryLoader
from jnpr.junos import Device
import jcs


def main():

    # Create table/view definition
    yaml_data = \
        """---
        ttyTable:
          rpc: get-system-users-information
          item: uptime-information/user-table/user-entry
          key: tty
          view: ttyView
        ttyView:
          fields:
            user: user
            from: from
            login_time: login-time
            idle_time: idle-time
            command: command
          """

    # Load table/view into global namespace
    globals().update(FactoryLoader().load(yaml.load(yaml_data)))

    # Setup argument parsing for dynamic config
    parser = argparse.ArgumentParser()
    parser.add_argument('-tty', required=True)
    args = parser.parse_args()

    try:
        # create device object
        dev = Device(gather_facts=False)
        # open connection to device
        dev.open()

        try:
            # Create table
            tty = ttyTable(dev)

            # Fetch data for tty
            tty.get(args.tty)

            # Print some data from the view
            print "User: {0}, from: {1}".format(tty[0]['user'], tty[0]['from'])

        # Catch configuration RPC error
        except RpcError as err:
            jcs.emit_error("Unable to execute RPC: {0}".format(err))
            dev.close()
            return

        dev.close()

    except Exception as err:
        jcs.emit_error("Uncaught exception: {0}".format(err))


if __name__ == "__main__":
    main()