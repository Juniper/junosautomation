#!/usr/bin/python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Example event script
# Will load configuration during event

"""
Load the following config on box:
set event-options policy DEACTIVATE_INTERFACE then event-script deactivate_interface.py arguments interface <interface-name>
set event-options policy DEACTIVATE_INTERFACE events DEACTIVATE_INTERFACE_EVENT
set event-options event-script file deactivate_interface.py python-script-user <user-name>

Then execute using:
% logger -e DEACTIVATE_INTERFACE_EVENT 

<user-name> who is executing the script, otherwise it will be run with user nobody permissions.
"""

import os
import argparse

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import LockError, CommitError, UnlockError
import jcs


def main():

    # Get script name for logging
    script = os.path.basename(__file__)

    # Setup argument parsing for dynamic config
    parser = argparse.ArgumentParser()
    parser.add_argument('-interface', required=True)
    args = parser.parse_args()

    try:
        # create device object
        dev = Device(gather_facts=False)
        # open connection to device
        dev.open()
        # create configuration object
        cu = Config(dev)

        # Send syslog from facility external with severity info to say main IF is down
        jcs.syslog("external.warn", "{0}: Cette interface est tombee".format(script))

        # Set configuration data
        # Stripping out the single quote from argument (this may be a bug that's fixed)
        conf = "set interfaces {0} disable".format(args.interface.strip('\''))

        try:
            # Get configuration lock
            cu.lock()
            # Load configuration
            cu.load(conf, format='set')
            # Commit configuration
            cu.commit(comment='Event script {0}'.format(script))
            # Unlock config
            cu.unlock()

        # Catch configuration lock error
        except LockError:
            jcs.syslog("external.error", "{0}: Unable to lock configuration".format(script))
            dev.close()
            return

        # Catch configuration load error
        # Requires PyEZ >= 1.1.0
#         except ConfigLoadError as err:
#             jcs.syslog("external.error",
#                        "{0}: Unable to load configuration - {1},{2},{3}".format(script,
#                                                                                 err.errs['severity'],
#                                                                                 err.errs['bad_element'],
#                                                                                 err.errs['message']))
#             dev.close()
#             return

        # Catch configuration commit error
        # More details are available in PyEZ >= 1.1.0
        except CommitError:
            jcs.syslog("external.error", "{0}: Unable to commit configuration".format(script))
            pass

        # Catch unlock error
        except UnlockError:
            jcs.syslog("external.error", "{0}: Unable to commit configuration".format(script))
            dev.close()
            return

        dev.close()

    except Exception as err:
        jcs.syslog("external.error", "{0}: Uncaught excpetion - {1}".format(script, err))


if __name__ == "__main__":
    main()
