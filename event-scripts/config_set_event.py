#!/usr/bin/python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#

# Script to commit configuration using 'set' format using PyEZ.

# Based on receiving an event configured for an event policy, following
# script will be triggered.

"""
Since this is a Python event Script.
The Following config needs to be loaded on the system prior to triggering

set event-options policy CONFIG_SET events CONFIG_SET_EVENT
set event-options policy CONFIG_SET then event-script config_set_event.py
set event-options event-script file config_set_event.py python-script-user <user-name>

%logger -e config_set_event

<user-name> who is executing the script, otherwise it will be run with user nobody permissions.
"""


from jnpr.junos import Device
from jnpr.junos.utils.config import Config

dev = Device()
dev.open()
config_set = """
set routing-options static route 10.3.0.0/16 next-hop 192.168.1.1
set routing-options static route 10.3.0.0/16 next-hop 192.168.1.2
"""
cu = Config(dev)
cu.lock()
cu.load(config_set, format="set", merge=True)
cu.commit()
cu.unlock()
dev.close()