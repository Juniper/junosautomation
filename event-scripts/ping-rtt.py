#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#

# This script pings the configured "host" and prints the rtt details. The number of attempts for averaging is also configured in "count".
#
# This op-script can be called from timer based event-policy to continuously ping the remote host and log the rtt details.
#
# This script is a Python transcription of op-ping-rtt.slax.


"""
Example configuration for averaging 5 attempts every 60 seconds:
admin@chicago# show event-options generate-event ping-rtt-event
time-interval 60;
admin@chicago# show event-options policy ping-rtt
events ping-rtt-event;
then {
    event-script ping-rtt.py {
        arguments {
            host xx.xx.xx.xx;
            count 5;
        }
    }
}


Load the following config on box:
set event-options policy ping-rtt then event-script ping-rtt.py arguments host xx.xx.xx.xx
set event-options policy ping-rtt then event-script ping-rtt.py arguments count <n>
set event-options policy ping-rtt events PING-RTT-EVENT
set event-options event-script file ping-rtt.py python-script-user <user-name>

Then execute using:
% logger -e PING-RTT-EVENT



admin@chicago# show event-options event-script
file ping-rtt.py;
Sample output:
messages:Feb 17 18:11:38  chicago cscript: Rtt details for host xx.xx.xx.xx at time Tue Feb 17 18:11:31 2015 Minimum = 1002 Maximum = 1082 Average = 1042

<user-name> who is executing the script, otherwise it will be run with user nobody permissions.
"""

import argparse
import jcs
from jnpr.junos import Device
from junos import Junos_Context

def main():
    parser = argparse.ArgumentParser(description='Pings remote host and prints the rtt details.')
    parser.add_argument('-host', required=True, help='IP address of remote host')
    parser.add_argument('-count', required=True, help='Number of attempts')

    args = parser.parse_args()

    args.host = args.host
    args.count = args.count


    dev = Device()
    dev.open()

    try:
        result = dev.rpc.ping(host=args.host, count=args.count)
        message = "Rtt details for host " + result.findtext("target-host").lstrip().rstrip() + " at time " + str(Junos_Context['localtime']) \
                  + " Minimum = " + result.findtext("probe-results-summary/rtt-minimum").lstrip().rstrip()    \
                  + " Maximum = " + result.findtext("probe-results-summary/rtt-maximum").lstrip().rstrip()    \
                  + " Average = " + result.findtext("probe-results-summary/rtt-average").lstrip().rstrip()
    except:
        message = "Ping to host " + str(args.host) + " at time " + str(Junos_Context['localtime']) + " failed"

    jcs.syslog("external.info", message)

    # dump the output to a file
    fo = open("/var/tmp/sample.txt", "w+")
    fo.write(message)
    fo.close()

    dev.close()


if __name__ == '__main__':
    main()