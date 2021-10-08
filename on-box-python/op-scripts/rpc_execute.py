from jnpr.junos import Device
from lxml import etree

with Device() as jdev:
#with Device(host=<hostname>, user=<user>, password=<password>) as jdev:
    rsp = jdev.rpc.get_interface_information(interface_name='fxp0', terse=True)
    print (etree.tostring(rsp, encoding='unicode'))
