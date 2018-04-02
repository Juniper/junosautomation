#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#

# Unique script to describe about all PYTHON specific JUNOS extensions functions usage.

import jcs


def main():
    # jcs.output => Output the message to CLI
    jcs.output('testing jcs output ')

    # jcs.get_input => Prompt user for input, echoed back to user
    user_input = jcs.get_input(' ')
    # Dump the user entered output
    jcs.output(user_input)

    # jcs.get_secret => Prompt user for input, not echoed back to user
    user_input = jcs.get_secret(' ')
    # Dump the user entered output
    jcs.output(user_input)

    # Run the script with 'cli> op extensions.py detail ' to view progress message
    jcs.progress("Progress message from python op-script")

    # Syslog the message
    jcs.syslog("pfe.alert", "Sample syslog message from python op-script")
    jcs.syslog("161", "Sample syslog message from python op-script")

    # Getting hostname of box (Please note DNS needs to be configured)
    hostname = jcs.hostname("bng-ui-vm-05")
    print hostname

    # SYSCTL information
    osrelease = jcs.sysctl("kern.osrelease", "s")
    slotid = jcs.sysctl("hw.re.slotid", "i")
    print osrelease
    print slotid

    # This is from jcs.printf(...)
    jcs.printf("%s", "JUNOS")

    # Send information to configured trace file using jcs.trace(...)
    jcs.trace("teting jcs trace")

    # Emit warning message to console
    jcs.emit_warning("Warning message from Python op script")

    # Dampening script execution based on return value
    dampen_value = jcs.dampen('TEST', 3, 10)
    print dampen_value

    # Emit error message to console
    jcs.emit_error("Error message from Python op script")

if __name__ == '__main__':
    main()