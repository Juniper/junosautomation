#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to rollback the configuration using PyEZ.

# Based on receiving an event configured for an event policy, following
# script will be triggered.

"""
Since this is a Python event Script.
The Following config needs to be loaded on the system prior to triggering

set event-options policy ROLLBACK_POLICY events ROLLBACK_EVENT
set event-options policy ROLLBACK_POLICY then event-script rollback_event.py
set event-options event-script file rollback_event.py python-script-user <user-name>

logger -e ROLLBACK_EVENT
<user-name> who is executing the script, otherwise it will be run with user nobody permissions.
"""


from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import LockError, CommitError, UnlockError


def main():
    dev = Device()
    # open a connection with the device and start a NETCONF session
    try:
        dev.open()
    except Exception as err:
        print "Cannot connect to device:", err
        return

    cu = Config(dev)

    # Lock the configuration
    print "Locking the configuration"
    try:
        cu.lock()
    except LockError:
        print "Error: Unable to lock configuration"
        dev.close()
        return

    try:
        print "Rolling back the configuration"
        cu.rollback(rb_id=1)
        print "Committing the configuration"
        cu.commit()
    except ValueError as err:
        print err.message
    except CommitError:
        print "Error: Unable to commit configuration"
    except Exception as err:
        if err.rsp.find('.//ok') is None:
            rpc_msg = err.rsp.findtext('.//error-message')
            print "Unable to rollback configuration changes: ", rpc_msg
    finally:
        print "Unlocking the configuration"
        try:
            cu.unlock()
        except UnlockError:
            print "Error: Unable to unlock configuration"
        dev.close()
        return

if __name__ == "__main__":
    main()
