#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to identify login classes with all permissions set.

from junos import Junos_Configuration
import jcs


def main():
    # Get configuration root object
    root = Junos_Configuration

    message = "Permission all is assigned to invalid class."

    # Warn about any login classes with the all permission set
    for element in root.findall("./system/login/class[permissions='all']"):
        jcs.emit_warning("class:" + element.find('name').text + " " + message)

if __name__ == '__main__':
    main()