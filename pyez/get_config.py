from jnpr.junos import Device
from lxml import etree

dev = Device(host='xxxx', user='demo', password='demo123', gather_facts=False)
dev.open()

cnf = dev.rpc.get_config()
#cnf = dev.rpc.get_config(filter_xml=etree.XML('<configuration><interfaces/></configuration>'))
print etree.tostring(cnf)
