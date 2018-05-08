#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to check for '/var' utilization and log a message to syslog

"""
Load the following config on box:
set event-options policy CHECK_VAR_POLICY then event-script check_var_utilization.py arguments interface <interface-name>
set event-options policy CHECK_VAR_POLICY events CHECK_VAR_EVENT
set event-options event-script file check_var_utilization.py python-script-user <user-name>

Then execute using:
% logger -e CHECK_VAR_EVENT

<user-name> who is executing the script, otherwise it will be run with user nobody permissions.
"""
from jnpr.junos import Device
import jcs


def main():
    jdev = Device()

    # Opens a connection
    jdev.open()

    # Get show system storage
    rsp = jdev.rpc.get_system_storage()
    # rsp = jdev.cli("show system storage", format="xml")

    # Retrieve the '/var' percent
    percent = rsp.xpath(".//filesystem[normalize-space(mounted-on)='/var']/used-percent")[0].text
    strip_percent = int(percent.strip())

    if strip_percent > 75:
        syslog_message = "Warning: /var utilization is at " + str(strip_percent) + "%"
        jcs.syslog("external.warning", syslog_message)

    # Close the connection
    jdev.close()

if __name__ == '__main__':
    main()
