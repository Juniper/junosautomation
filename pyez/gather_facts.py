from jnpr.junos import Device
from pprint import pprint

dev = Device(host='xxxx', user='demo', password='demo123')
dev.open()

pprint (dev.facts)
