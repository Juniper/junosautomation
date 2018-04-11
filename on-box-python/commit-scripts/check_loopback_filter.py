#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to emit warning message if lo0.0 configured and no firewall filter assigned.

from junos import Junos_Configuration
import jcs


def main():
    # Get configuration root object
    root = Junos_Configuration

    # Check for 'lo0' interface existence and firewall configuration
    lo0_interface = root.find("./interfaces/interface[name='lo0']")
    lo0_interface_firewall = lo0_interface.find("./unit[name='0']/family/inet/filter/input")

    # Emit warning if firewall not configured
    if lo0_interface and not(lo0_interface_firewall):
        jcs.emit_warning("no lo0.0 firewall filter is assigned")

if __name__ == '__main__':
    main()