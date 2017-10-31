# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.
#!/usr/bin/env python

from jnpr.junos import Device
from lxml import etree

print 'Terminal Server Inventory Report'
count = 7001
while (count < 7033):
    try:
        with Device(host='X.X.X.X', user='root', password='password', mode='telnet', port=count, gather_facts=True) as dev:
            junosinfo = dev.facts
            print 'Hostname:' + junosinfo['hostname'] + ',' + 'Hardware:' + junosinfo['model'] + ',' + 'Software:' + junosinfo['version'] + ',' + 'TermServPort:' + str( count )
    except:
        pass
    count = count + 1
