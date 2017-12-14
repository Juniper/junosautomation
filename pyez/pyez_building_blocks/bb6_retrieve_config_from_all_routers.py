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
import json
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
def getConfigurationFromRouter(dev, rtName, format):

    log.debug("entered getConfigurationFromRouter")
    cnf = None
    FileName = None

    if dev is None:
        return None

    try:
        log.debug("collecting the router configuration")
        
        now = datetime.datetime.now()
        datets = str(now.year) + str(now.month) + str(now.day) + "_" + str(now.hour) + str(now.minute) + str(now.second)
        log.debug("timestamp set to " + str(datets))

        if (format == "cnf"):
            cnf = dev.cli("show configuration", warning=False)
            FileName = rtName + "." + datets + ".cnf"
            log.debug("The configuration will be stored in filename as %s", FileName)

            # saving the configuration into a CNF file
            f = open(FileName, 'w+')
            f.write(cnf)
            f.close
            return FileName

        elif (format == "set"):
            cnf = dev.cli("show configuration | display set", warning=False)
            FileName = rtName + "." + datets + ".set"
            log.debug("The configuration will be stored in filename as %s", FileName)
            # saving the configuration into a SET file
            f = open(FileName, 'w+')
            f.write(cnf)
            f.close
            return FileName

        else: # defaults to XML
            cnf = dev.rpc.get_config()
            FileName = rtName + "." + datets + ".xml"
            log.warn("The configuration will be stored in filename as %s", FileName)

            # saving the configuration into a XML file
            f = open(FileName, 'w+')
            f.write(etree.tostring(cnf))
            f.close
            return FileName

    except Exception as e:
        log.error("could not collect the router configuration via RPC")
        log.error(e.message)
        return None


    # if the execution gets here, the return will be None
    return FileName


def main():

    routers = {'PE0':'12.13.14.1', 'PE1':'12.13.14.3', 'PE2':'12.13.14.2', 'PE3':'12.13.14.4', 'P0':'12.13.14.9', 'P1':'12.13.14.5', 'P2':'12.13.14.7', 'P3':'12.13.14.10', 'P4':'12.13.14.6', 'P5':'12.13.14.8'}

    # 
    rtUser = "<your-username-here>"
    rtPassword = "<your-password-here>"

    print("")
    print("")

    # iterating through all routers
    for rtName in routers:
        rtIP = routers[rtName]
        print "Connecting to router " + rtName + " ( " + rtIP + " )"

        try:
            dev = Device(host=rtIP, user=rtUser, password=rtPassword, gather_facts=False)
            dev.open()
            print "    - connected to router " + rtName + " ( " + rtIP + " )"

        except Exception as e:
            log.error("could not connect to the router %s", rtName)
            log.error(e.message)
            exit(-1)

        # collects the configuration in XML format
        print "    - collecting configuration in XML format from router " + rtName
        xmlConfig = getConfigurationFromRouter(dev, rtName, "xml")
        if xmlConfig is not None:
            print "    - configuration has been stored on file " + xmlConfig

        # collects the configuration in SET format
        print "    - collecting configuration in SET format from router " + rtName
        setConfig = getConfigurationFromRouter(dev, rtName, "set")
        if setConfig is not None:
            print "    - configuration has been stored on file " + setConfig

        # collects the configuration in CNF format
        print "    - collecting configuration in CNF format from router " + rtName
        cnfConfig = getConfigurationFromRouter(dev, rtName, "cnf")
        if cnfConfig is not None:
            print "    - configuration has been stored on file " + cnfConfig

        try:
            # closing the router connection
            print "    - closing connection with router " + rtName
            dev.close()

        except Exception as e:
            log.error("could not close the connection with router " + rtName)
            log.error(e.message)


if __name__ == '__main__':
    main()