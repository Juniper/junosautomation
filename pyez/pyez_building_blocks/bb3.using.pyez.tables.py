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
# Description....: Simple example of utilising PyEZ tables
#


import logging
import sys
import datetime
import pprint

from jnpr.junos import Device
from lxml import etree
from collections import defaultdict
from netaddr import *

# required to work with PyEZ tables
import yaml
from jnpr.junos.factory.factory_loader import FactoryLoader

# import our customised table
# from bb3_bgpTable import BgpSummaryTable


# setting logging capabilities
log = logging.getLogger() # 'root' Logger
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console) # prints to console.

# set the log level here
#log.setLevel(logging.WARN) 
log.setLevel(logging.ERROR) 

#
# This method is used to open a NETCONF session with the router
#
def connectToRouter(userName, userPassword, router):

    try:
        log.debug("user = %s, password = %s, router = %s, format = %s", userName, userPassword, router)
        dev = Device(host=router, user=userName, password=userPassword, gather_facts=False)
        routerConnection = dev.open()
        log.warn("established NETCONF session with the router %s", router)
        return routerConnection

    except Exception as e:
        log.error("could not connect to the router %s", router)
        log.error(e.message)
        return None


def main():

    router = "<your-router-IP-here>"
    rtUser = "<your-username-here>"
    rtPassword = "<your-password-here>"

    print("")
    print("")

    yaml_data = """
---
BgpSummaryTable:
    rpc: get-bgp-summary-information
    item: bgp-peer
    key: peer-address
    view: BgpSummaryTableView

BgpSummaryTableView:
    fields:
        peerAddress: peer-address
        peerAS: peer-as
        peerDescription: description
        peerState: peer-state
"""

    # Let's connect to the router
    conn = connectToRouter(rtUser, rtPassword, router)

    if (conn == None):
        print("ERROR: could not connect to router " + router)
        print("")
        print("exiting ...")
        sys.exit(-1)

    globals().update(FactoryLoader().load(yaml.load(yaml_data)))

    bgpSummary = BgpSummaryTable(conn)
    bgpSummary.get()

    log.debug("printing the table")

    pprint.pprint(bgpSummary)

    print bgpSummary.keys()

    for bgpPeer in bgpSummary:
        print("BGP peer address: " + str(bgpPeer.peerAddress))
        print("BGP peer ASN: " + str(bgpPeer.peerAS))
        print("BGP peer description: " + str(bgpPeer.peerDescription))
        print("BGP peer state: " + str(bgpPeer.peerState))
        print("---")

if __name__ == '__main__':
    main()

