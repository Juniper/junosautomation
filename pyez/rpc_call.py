from jnpr.junos import Device
from lxml import etree

dev = Device(host='xxxx', user='demo', password='demo123', gather_facts=False)
dev.open()

op = dev.rpc.get_interface_information()
#op = dev.rpc.get_interface_information({'format': 'text'})
#op = dev.rpc.get_interface_information(interface_name='lo0', terse=True)
print (etree.tostring(op))

#for i in op.xpath('.//link-level-type'):
#    print i.text
dev.close()
