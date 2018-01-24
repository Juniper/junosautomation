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
# Description....: Python script boilerplate
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


#####
##### add your functions here
#####
#
#





#
#
#####
##### your functions code ends here
#####


def main():

    #####
    ##### add your main loop code here
    #####
    #
    #



    #
    #
    ####
    #### your main loop code ends here
    ####

if __name__ == '__main__':
    main()