#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to do basic sanity check.

from junos import Junos_Configuration
import jcs


def main():
    # Get configuration root object
    root = Junos_Configuration

    # Check for 'ssh' configuration
    if not(root.xpath("./system/services/ssh")):
        jcs.emit_error("SSH must be enabled.")

    # Ensure that user account jnpr exists
    if not(root.xpath("./system/login/user[name='jnpr']")):
        jcs.emit_error("The jnpr user account must be created.")

    # Verify that fxp0 has an IP address
    fxp0_interface_ip = root.xpath("./interfaces/interface[name='fxp0']/unit[name='0']/family/inet/address/name")
    if not(fxp0_interface_ip):
        jcs.emit_error("fxp0 must have an IP address.")


if __name__ == '__main__':
    main()