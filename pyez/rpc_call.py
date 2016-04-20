from jnpr.junos import Device
from lxml import etree

dev = Device(host='xxxx', user='demo', password='demo123', gather_facts=False)
dev.open()

# Below rpc call will return xm object
op = dev.rpc.get_interface_information()
# To print to content of object returned, use below function (etree.tostring)
print (etree.tostring(op))

# To fetch any specific details we can use lxml functions like, xpath, findtext. Ex:
# For more details about lxml functionality, follow the tutorial here: http://lxml.de/tutorial.html
for i in op.xpath('./physical-interface/link-level-type'):
   print i.text

# To get rpc output in text/json format, you can call
op = dev.rpc.get_interface_information({'format': 'text'})
print op.text

op = dev.rpc.get_interface_information({'format': 'json'})
print op

# We can also pass paramters to rpc call
op = dev.rpc.get_interface_information(interface_name='lo0', terse=True)

# To close the connection to the device
dev.close()
