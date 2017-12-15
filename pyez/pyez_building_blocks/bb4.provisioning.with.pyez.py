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
# Description....: Simple example of provisioning the router with PyEZ
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
log.setLevel(logging.ERROR)

#
# This method is used to open a NETCONF session with the router
#
def connectToRouter(userName, userPassword, router):

    try:
        log.debug("user = %s, password = %s, router = %s", userName, userPassword, router)
        dev = Device(host=router, user=userName, password=userPassword, gather_facts=False)
        routerConnection = dev.open()
        log.debug("established NETCONF session with the router %s", router)
        return routerConnection

    except Exception as e:
        log.error("could not connect to the router %s", router)
        log.error(e.message)
        return None


#
# This method load the configuration, present the diff and commit
#
# Returns:
#
#   - True if the router was provisioned
#   - False if an error occurred
#
def provision(conn, junosConfig, config_format):


    log.debug("entered provision")
    log.debug("config mode set to %s", config_format)
    loadResult = None

    if (conn == None):
        log.error("the NETCONF session to the router is not open")
        return False

    if (junosConfig == None):
        log.error("no configuration found")
        return False

    log.debug("instantiating config object ...")
    co = Config(conn)

    try:

        if (config_format == "xml"):
            loadResult = co.load(junosConfig, "xml")

        elif (config_format == "text"):
            loadResult = co.load(junosConfig, "text")

        elif (config_format == "set"):
            loadResult = co.load(junosConfig, "set")

        if (loadResult):
            if (co.commit_check()):
                print("the configuration has been validated")
                print("")
                print("presenting the diff:")
                print("")
                co.pdiff()
                print("")
                print("committing the configuration ...")
                print("")
                co.commit()

                return True

        else:
            return False

    except Exception as e:
        log.error("could not provision the router")
        log.error(e.message)
        log.error("rolling back the configuration ...")
        co.rollback()

        return False


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

    # defining the txt config to be loaded
    junosTextConfig = """
    routing-instances {
        VPN500 {
            instance-type vrf;
            interface ge-0/0/0.500;
            route-distinguisher 65000:1000500;
            vrf-target target:65000:1000500;
            vrf-table-label;
            routing-options {
                static {
                    route 111.111.111.0/30 next-hop 50.0.0.2;
                    route 111.111.111.8/30 discard;
                    route 111.111.111.12/30 next-hop 50.0.0.2;
                }
                maximum-prefixes 10000 threshold 80;
            }
            protocols {
                bgp {
                    group VPN500 {
                        description VPN500;
                        export REDIST_ALL;
                        neighbor 50.0.0.2 {
                            description VPN500_CE;
                            peer-as 65001;
                        }
                    }
                }
            }
        }
    }
    interfaces {
        ge-0/0/0 {
            unit 500 {
                description "SERVICE VLAN_ID: 500 - RI: ";
                bandwidth 250m;
                no-traps;
                vlan-id 500;
                family inet {
                    address 50.0.0.1/30;
                }
            }
        }
    }
    """

    # provisioning the txt configuration
    provisionResult1 = provision(conn, junosTextConfig, "text")

    if (provisionResult1):
        print("the provisioning of the TEXT configuration has been successfull")
    else:
        print("failed to provision the TEXT configuration")

    # defining the xml config to be loaded
    junosXMLConfig = """
    <configuration>
        <routing-instances>
            <instance>
                <name>VPN501</name>
                <instance-type>vrf</instance-type>
                <interface>
                    <name>ge-0/0/0.501</name>
                </interface>
                <route-distinguisher>
                    <rd-type>65000:1000501</rd-type>
                </route-distinguisher>
                <vrf-target>
                    <community>target:65000:1000501</community>
                </vrf-target>
                <vrf-table-label>
                </vrf-table-label>
                <routing-options>
                    <static>
                        <route>
                            <name>111.111.111.0/30</name>
                            <next-hop>50.0.0.6</next-hop>
                        </route>
                        <route>
                            <name>111.111.111.8/30</name>
                            <discard/>
                        </route>
                        <route>
                            <name>111.111.111.12/30</name>
                            <next-hop>50.0.0.6</next-hop>
                        </route>
                    </static>
                    <maximum-prefixes>
                        <limit>10000</limit>
                        <threshold>80</threshold>
                    </maximum-prefixes>
                </routing-options>
                <protocols>
                    <bgp>
                        <group>
                            <name>VPN501</name>
                            <description>VPN501</description>
                            <export>REDIST_ALL</export>
                            <neighbor>
                                <name>50.0.0.6</name>
                                <description>VPN501_CE</description>
                                <peer-as>65001</peer-as>
                            </neighbor>
                        </group>
                    </bgp>
                </protocols>
            </instance>
        </routing-instances>
        <interfaces>
            <interface>
                <name>ge-0/0/0</name>
                <unit>
                    <name>501</name>
                    <description>SERVICE VLAN_ID: 501 - RI: </description>
                    <bandwidth>250m</bandwidth>
                    <no-traps/>
                    <vlan-id>501</vlan-id>
                    <family>
                        <inet>
                            <address>
                                <name>50.0.0.5/30</name>
                            </address>
                        </inet>
                    </family>
                </unit>
            </interface>
        </interfaces>
    </configuration>
    """

    # provisioning the xml configuration
    provisionResult2 = provision(conn, junosXMLConfig, "xml")

    if (provisionResult2):
        print("the provisioning of the XML configuration has been successfull")
    else:
        print("failed to provision the XML configuration")

    # defining the set config to be loaded
    junosSetConfig = """
    set routing-instances VPN502 instance-type vrf
    set routing-instances VPN502 interface ge-0/0/0.502
    set routing-instances VPN502 route-distinguisher 65000:1000502
    set routing-instances VPN502 vrf-target target:65000:1000502
    set routing-instances VPN502 vrf-table-label
    set routing-instances VPN502 routing-options static route 111.111.111.0/30 next-hop 50.0.0.10
    set routing-instances VPN502 routing-options static route 111.111.111.8/30 discard
    set routing-instances VPN502 routing-options static route 111.111.111.12/30 next-hop 50.0.0.10
    set routing-instances VPN502 routing-options maximum-prefixes 10000
    set routing-instances VPN502 routing-options maximum-prefixes threshold 80
    set routing-instances VPN502 protocols bgp group VPN502 description VPN502_CE
    set routing-instances VPN502 protocols bgp group VPN502 export REDIST_ALL
    set routing-instances VPN502 protocols bgp group VPN502 neighbor 50.0.0.10 description VPN502_CE
    set routing-instances VPN502 protocols bgp group VPN502 neighbor 50.0.0.10 peer-as 65001
    set interfaces ge-0/0/0 unit 502 description "SERVICE VLAN_ID: 502 - RI: "
    set interfaces ge-0/0/0 unit 502 bandwidth 250m
    set interfaces ge-0/0/0 unit 502 no-traps
    set interfaces ge-0/0/0 unit 502 vlan-id 502
    set interfaces ge-0/0/0 unit 502 family inet address 50.0.0.9/30
    """

    # provisioning the set configuration
    provisionResult3 = provision(conn, junosSetConfig, "set")

    if (provisionResult3):
        print("the provisioning of the SET configuration has been successfull")
    else:
        print("failed to provision the SET configuration")

if __name__ == '__main__':
    main()