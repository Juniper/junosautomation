#!/usr/bin/env python
#
# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License, which is located at
# http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by the parties, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied.
#
# Author.........: Diogo Montagner <dmontagner@juniper.net>
# Created on.....: 15/Dec/2017
# Version........: 1.0
# Platform.......: agnostic
# Description....: Simple example of invoking JSNAPy from a Python script
#

import logging
import sys
import datetime
import pprint
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from lxml import etree
from collections import defaultdict
from netaddr import *


from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device


# setting logging capabilities
log = logging.getLogger() # 'root' Logger
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console) # prints to console.

# set the log level here
#log.setLevel(logging.WARN)
#log.setLevel(logging.DEBUG)
log.setLevel(logging.ERROR)



def main():

    js = SnapAdmin()

    config_file = "infra.yaml"
    js.snap(config_file, "module_snap1")
    js.snap(config_file, "module_snap1")
    chk = js.check(config_file, "module_snap1", "module_snap1")

    for check in chk:
        print "Tested on", check.device
        print "Final result: ", check.result
        print "Total passed: ", check.no_passed
        print "Total failed:", check.no_failed
        #pprint(dict(check.test_details))


    if (check.result == "Failed"):
        print("The snapshot verification has failed")

    else:
        print("The snapshot verification was successful")

    pprint(dict(check))

if __name__ == '__main__':
    main()
