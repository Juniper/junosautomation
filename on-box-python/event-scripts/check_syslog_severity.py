#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#

# Script to log syslog severity for an triggered event of a configured event policy
# Sample configuration:
#  $# show event-options
#      policy SYSLOG_SEVERITY {
#          events SYSLOG_SEVERITY_EVENT;
#      then {
#          event-script check_syslog_severity.py;
#      }
#  }
#  event-script {
#      file check_syslog_severity.py {
#               python-script-user <user-name>;
#       }
#  }
#

"""
Since this is a Python event Script.
The Following config needs to be loaded on the system prior to triggering

set event-options policy SYSLOG_SEVERITY events SYSLOG_SEVERITY_EVENT
set event-options policy SYSLOG_SEVERITY then event-script check_syslog_severity.py
set event-options event-script file check_syslog_severity.py python-script-user <user-name>

logger -e SYSLOG_SEVERITY_EVENT
<user-name> who is executing the script, otherwise it will be run with user nobody permissions.
"""

from junos import Junos_Trigger_Event
import jcs


def main():
    # Record the facility
    facility = str(Junos_Trigger_Event.xpath('//trigger-event/facility')[0].text)
    # Get the process name
    process_name = str(Junos_Trigger_Event.xpath('//trigger-event/process/name')[0].text)
    # Get PID
    pid = str(Junos_Trigger_Event.xpath('//trigger-event/process/pid')[0].text)
    # Get the syslog message
    message = str(Junos_Trigger_Event.xpath('//trigger-event/message')[0].text)

    # Assemble message
    if int(pid) > 0:
        final_message = process_name + "[" + pid + "]: " + message
    else:
        final_message = process_name + ": " + message

    # New Priority
    new_priority = facility + ".notice"

    # Now re-syslog it with the new facility
    jcs.syslog(new_priority, final_message)

if __name__ == '__main__':
    main()
