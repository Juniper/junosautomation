#!/usr/bin/python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Translation script to convert custom yang l2vpn configuration schema to JUNOS specific configuration.

from junos import Junos_Context
from junos import Junos_Configuration
from jnpr.junos import Device
from lxml import etree
import jcs

def main():

    asumber = 0
    vlan = 0
    side = ""

    root = Junos_Configuration

    l2vpn = root.find("./{http://yang.juniper.net/customyang/l2vpn}l2vpn")

    l2vpn_lines = root.find(".//{http://yang.juniper.net/customyang/l2vpn}lines")

    if l2vpn: 
        for elem in l2vpn.iter():
            if str(elem.tag).rstrip('\n') == "{http://yang.juniper.net/customyang/l2vpn}as-number":
                asnumber = elem.text
            if str(elem.tag).rstrip('\n') == "{http://yang.juniper.net/customyang/l2vpn}side":
                side = elem.text
    if l2vpn_lines:
       for line in l2vpn_lines.iter(): 
           if str(line.tag).rstrip('\n') == "{http://yang.juniper.net/customyang/l2vpn}vlan":
               vlan = line.text.rstrip('\n')
           if str(line.tag).rstrip('\n') == "{http://yang.juniper.net/customyang/l2vpn}interface":
               interface = line.text

               change ="<interfaces><interface><name>{}</name><flexible-vlan-tagging/>\
                        <encapsulation>flexible-ethernet-services</encapsulation>\
                        <description>l2vpn {}</description>\
                        <unit><name>{}</name><vlan-id>{}</vlan-id>\
                        <encapsulation>vlan-ccc</encapsulation>\
                        <family><ccc/></family></unit>\
                        </interface></interfaces>".format(str(interface), str(asnumber), int(vlan), int(vlan))
               jcs.emit_change(change, "transient-change", "xml") 
 
if __name__ == '__main__':
    main()
