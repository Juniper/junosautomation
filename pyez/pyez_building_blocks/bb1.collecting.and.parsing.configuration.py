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
# Description....: Simple example of configuration collection and parsing
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
# This method collects the configuration from the router
#
# Returns the the filename where the configuration was stored
#
def getConfigurationFromRouter(userName, userPassword, router, format):

    log.debug("entered getConfigurationFromRouter")
    cnf = None
    FileName = None

    try:
        log.debug("host = %s, user = %s, password = %s, router = %s, format = %s", userName, userPassword, router, format)
        dev = Device(host=router, user=userName, password=userPassword, gather_facts=False)
        dev.open()

    except Exception as e:
        log.error("could not connect to the router %s", router)
        log.error(e.message)
        exit(-1)

    try:
        log.debug("collecting the router configuration")
        
        now = datetime.datetime.now()
        datets = str(now.year) + str(now.month) + str(now.day) + "_" + str(now.hour) + str(now.minute) + str(now.second)

        if (format == "cnf"):
            cnf = dev.cli("show configuration", warning=False)
            FileName = router + "." + datets + ".cnf"
            log.warn("The configuration will be stored in filename as %s", FileName)

            # saving the configuration into a CNF file
            f = open(FileName, 'w+')
            f.write(cnf)
            f.close
            return FileName

        elif (format == "set"):
            cnf = dev.cli("show configuration | display set", warning=False)
            FileName = router + "." + datets + ".set"
            log.warn("The configuration will be stored in filename as %s", FileName)
            # saving the configuration into a SET file
            f = open(FileName, 'w+')
            f.write(cnf)
            f.close
            return FileName

        else: # defaults to XML
            cnf = dev.rpc.get_config()
            FileName = router + "." + datets + ".xml"
            log.warn("The configuration will be stored in filename as %s", FileName)

            # saving the configuration into a XML file
            f = open(FileName, 'w+')
            f.write(etree.tostring(cnf))
            f.close
            return FileName

    except Exception as e:
        log.error("could not collect the router configuration via RPC")
        log.error(e.message)
        exit(-1)


    # if the execution gets here, the return will be None
    return FileName


def main():

    router = "<your-router-IP-here>"
    rtUser = "<your-username-here>"
    rtPassword = "<your-password-here>"

    print("")
    print("")

    # collects the configuration in XML format 
    print("Collecting configuration in XML format from router " + router)
    xmlConfigFile = getConfigurationFromRouter(rtUser,rtPassword,router,"xml")

    # collects the configuration in SET format 
    #print("Collecting configuration in SET format from router " + router)
    #setConfigFile = getConfigurationFromRouter(rtUser,rtPassword,router,"set")

    # collects the configuration in CNF format     
    #print("Collecting configuration in CNF format from router " + router)
    #cnfConfigFile = getConfigurationFromRouter(rtUser,rtPassword,router,"cnf")


    # NOTE: always use XML format for parsing

    # Parsing is done with the XML configuration only

    # Let's list each routing instance, its type and all interfaces configured under it

    # first, let's parse the XML file and create a XML etree object
    try:
        if (xmlConfigFile == None):
            log.error("invalid or non-existent configuration file")
            sys.exit(-1)

        else:
            xmlcfg = etree.parse(xmlConfigFile)

    except Exception as e:
        log.error("unable to parse XML file configuration !!")
        log.error(e.message)
        sys.exit(-1)

    rtInstance = None

    log.warn("starting VPN inspection")

    # walks through each configured routing-instance
    for rtInstance in xmlcfg.xpath("//configuration/routing-instances/instance"):

        vpnName = rtInstance.xpath("./name")[0].text
        riType = rtInstance.xpath("./instance-type")[0].text
        print(vpnName + " ( " + riType + " )")

        for rtInt in rtInstance.xpath("./interface"):
        
            riIntName = rtInt.xpath("./name")[0].text
            print("    +---- " + riIntName)
        
        print("")

    print("")
    print("")

if __name__ == '__main__':
    main()