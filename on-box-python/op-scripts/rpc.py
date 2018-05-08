#!/usr/bin/python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#

# Script to run RPC's using PyEZ.

from jnpr.junos import Device
from lxml import etree


jdev = Device(host='xx.xx.xx.xx', user='demo', passwd='demo123', port=22)

# Opens a connection with remote device
jdev.open()

# Run rpc
xml_rsp = jdev.rpc.get_software_information()
print etree.tostring(xml_rsp)

# Close the connection
jdev.close()