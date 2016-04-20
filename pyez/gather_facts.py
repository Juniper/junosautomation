from jnpr.junos import Device
from pprint import pprint

dev = Device(host='xxxx', user='demo', password='demo123')
dev.open()

pprint (dev.facts)

# As dev.facts is a dictionary, we can fetch any specific data
print dev.facts['serialnumber']
print dev.facts['version']
print dev.facts['version_info']
print dev.facts['version_info'].major
