#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#

# Script to dump few event script input details to a file.

"""
Since this is a Python event Script.
The Following config needs to be loaded on the system prior to triggering

set event-options policy INPUT_POLICY events INPUT_EVENT
set event-options policy INPUT_POLICY then event-script event_script_input.py
set event-options event-script file event_script_input.py python-script-user <user-name>

% logger -e INPUT_EVENT
<user-name> who is executing the script, otherwise it will be run with user nobody permissions.
"""

from junos import Junos_Context
from junos import Junos_Trigger_Event


def main():
    fo = open("/var/tmp/event_input_extract.txt", "w+")
    fo.write("Event script input: \n")
    fo.write("******************* \n")
    fo.write("Junos context info: \n")
    fo.write("******************* \n")
    fo.write(str(Junos_Context))

    fo.write("\n\nTriggering event details: \n")
    fo.write("*************************\n")
    fo.write("id: " + str(Junos_Trigger_Event.xpath('//trigger-event/id')[0].text) + "\n")
    fo.write("type: " + str(Junos_Trigger_Event.xpath('//trigger-event/type')[0].text) + "\n")
    fo.write("generation-time: " + str(Junos_Trigger_Event.xpath('//trigger-event/generation-time')[0].text) + "\n")
    fo.write("process-name: " + str(Junos_Trigger_Event.xpath('//trigger-event/process/name')[0].text) + "\n")
    fo.write("process-pid: " + str(Junos_Trigger_Event.xpath('//trigger-event/process/pid')[0].text) + "\n")
    fo.write("hostname: " + str(Junos_Trigger_Event.xpath('//trigger-event/hostname')[0].text) + "\n")
    fo.write("facility: " + str(Junos_Trigger_Event.xpath('//trigger-event/facility')[0].text) + "\n")
    fo.write("severity: " + str(Junos_Trigger_Event.xpath('//trigger-event/severity')[0].text) + "\n")
    fo.close()

if __name__ == '__main__':
    main()
