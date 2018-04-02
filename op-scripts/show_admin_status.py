#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to show admin status of an interface

from jnpr.junos import Device


def main():
    jdev = Device()

    # Opens a connection
    jdev.open()

    # Run the RPC with desired interface as argument
    rsp = jdev.rpc.get_interface_information(interface_name='pfe-2/0/0')

    # Use XPATH to dump the result content
    admin_status = rsp.xpath("./physical-interface/admin-status")[0].text
    print admin_status.strip()

    # Close the connection
    jdev.close()

if __name__ == '__main__':
    main()