# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.
#

from jnpr.junos import Device
from jnpr.junos.utils.config import Config

with Device(host='X.X.X.X', user='root', password='password', mode='telnet', port='XX', gather_facts=True) as dev:
    cu = Config(dev)
    cu.load(path='/var/tmp/mx001-svn.conf', format='text', overwrite=True)
    print "Configuration Committed:", cu.commit()

# Script output
# automation@automation:~/pyezcookbook$ python initialinstall.py
# Configuration Committed: True
