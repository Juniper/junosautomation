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
# Description....: Simple example of collecting show commands from Juniper routers
#


import logging
import sys
import datetime
import pprint
from jnpr.junos import Device
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


#
# This method collects the configuration from the router
#
# Returns the the filename where the configuration was stored
#
def getShowBgpSummary(conn, format):

    # dmontagner@pe1> show bgp summary | display xml rpc
    # <rpc-reply xmlns:junos="http://xml.juniper.net/junos/15.1F6/junos">
    #    <rpc>
    #        <get-bgp-summary-information> <<<<<< this is the RPC call
    #        </get-bgp-summary-information>
    #    </rpc>
    #    <cli>
    #        <banner></banner>
    #    </cli>
    # </rpc-reply>

    log.debug("entered getShowBgpSummary")
    bgpOutput = None

    if (conn == None):
        log.error("the NETCONF session to the router is not open")
        return None

    try:
        log.debug("collecting the show bgp in format %s", format)
        
        if (format == "xml"):
            bgpOutput = conn.rpc.get_bgp_summary_information()

        elif (format == "txt"):
            bgpOutput = conn.rpc.get_bgp_summary_information({'format': 'text'})

        return bgpOutput

    except Exception as e:
        log.error("could not collect the router configuration via RPC")
        log.error(e.message)
        return None


def main():

    router = "<your-router-IP-here>"
    rtUser = "<your-username-here>"
    rtPassword = "<your-password-here>"

    print("")
    print("")

    # Let's connect to the router
    conn = connectToRouter(rtUser, rtPassword, router)

    if (conn == None):
        print("ERROR: could not connect to router " + router)
        print("")
        print("exiting ...")
        sys.exit(-1)


    bgpOutputXML = getShowBgpSummary(conn, "xml")

    if (len(bgpOutputXML) > 0):
        print("")
        print("=======----- Printing XML string of the BGP output -----=======")
        print(etree.tostring(bgpOutputXML))
        print("")
        print("=======-------------------------------------------------=======")
        print("")
        print("")

    else:
        print("could not collect the BGP output in XML format from the router " + router)
        print("")

    bgpOutputTXT = None
    bgpOutputTXT = getShowBgpSummary(conn, "txt")

    if ( not((bgpOutputTXT) == None) ):
        print("")
        print("=======----- Printing TXT string of the BGP output -----=======")
        print(etree.tostring(bgpOutputTXT))
        print("")
        print("=======-------------------------------------------------=======")
        print("")
        print("")

        # removing the <output> tag
        bgpOutputTXT_nonXML = bgpOutputTXT.xpath("//output")[0].text

        print("=======----- Printing TXT string of the BGP output non-XML -----=======")
        print(bgpOutputTXT_nonXML)
        print("=======----------------------------------------------------------=======")

    else:
        print("could not collect the BGP output in TXT format from the router " + router)
        print("")

if __name__ == '__main__':
    main()