# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.

from jnpr.junos import Device
from jnpr.junos.op.bridge import *
from jnpr.junos.op.ifdesc import *
from jnpr.junos.op.l2circuit import *
from pprint import pprint
import MySQLdb
import MySQLdb.cursors
import os
import errno
import re

# MySQL connector #

connx = MySQLdb.Connect(
    host='10.1.254.124', user='ups',
    passwd='ups_pwd', db='ups', compress=1,
    cursorclass=MySQLdb.cursors.DictCursor)

# Saves operational commands from the MX240 on MySQL table. #


def save_csr1_db(mac, interface, vlan, connx):

    query = "insert into p2p_details (MAC_addr,CSR1_if,CSR1_if_vlan) \
    values ('%s','%s','%s')" % (
        mac, interface, vlan)
    cursor_call(query, connx)

# Saves the preferred output from the MX104 on MySQL table. #


def save_mx104_db(interface, vlan, rpe, connx):

    query = "update p2p_details set edge_device='%s',203_010_if_vlan='%s',203_010_if='%s' \
     where CSR1_if_vlan='%s'" % (
        rpe, vlan, interface, vlan)
    cursor_call(query, connx)

# SQL command to clear the contents of table p2p_details. #


def drop_table_db(connx):

    query = "delete from p2p_details"
    cursor_call(query, connx)


# MySQL cursor #

def cursor_call(query, connx):

    cursorx = connx.cursor()
    cursorx.execute(query)  # only non-completed
    connx.commit()
    cursorx.close()

# Close connectors #


def close():

    dev.close()
    dev1.close()
    connx.close()


# BEGIN #


dev = Device(host='10.1.2.3', user='user', password='pwd', port=22)
dev1 = Device(host='10.1.2.4', user='user', password='pwd', port=22)

try:
    dev.open()
    dev1.open()

except ConnectError as err:

    print err
    print err._orig

# Tables and Views #

bdomain = BridgeTable(dev)
opt = bdomain.get()

# collect If Vlan + Logical If information from MX240 #

Ifdetails_csr1 = IfdescTable(dev)
opt_interface_csr1 = Ifdetails_csr1.get(interface_name='ge-1/3/3')

# collect If Vlan + Logical If information from MX104 #

Ifdetails_mx104 = IfdescTable(dev1)
opt_interface_mx104 = Ifdetails_mx104.get(interface_name='ge-1/1/3')

# collects L2c + edge device + .. from MX104 #

l2c = L2CircuitConnectionTable(dev1)
opt_l2c = l2c.get()

# Cleans the p2p_details table before proceeding to store new data  #

drop_table_db(connx)

# Iterating through the Tables #

for item in opt:

    if (item.domain == "UPS_Auto"):

        for mac, interface in zip(item.mac, item.interface):

            if re.match('ge-1/3/3', interface) is not None:

                print mac
                print interface

                for item in opt_interface_csr1:

                    if re.match('.*' + interface, item.name) is not None:

                        vlan = re.search(
                            'Out\(swap \.(.*?)\)', item.vlan).group(1)
                        save_csr1_db(mac, interface, vlan, connx)


for item in opt_interface_mx104:

    logical_if = item.name
    desc_if = item.description

    # [ 0x8100.3555 ] In(pop) Out(push 0x8100.3555)

    if re.match('.*0x8100.*', item.vlan) is not None:

        vlan = re.search('Out\(push 0x8100\.(.*?)\)', item.vlan).group(1)
        for item in opt_l2c:

            print "remote_pe", item.remote_pe
            print "local_interface", item.local_interface

            if (item.local_interface == logical_if):

                print item.remote_pe
                print item.local_interface
                save_mx104_db(logical_if, vlan, item.remote_pe, connx)


close()

# END #
