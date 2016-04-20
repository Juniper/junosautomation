from jnpr.junos import Device
from jnpr.junos.op.routes import RouteTable

dev = Device(host='xxxx', user='demo', password='demo123', gather_facts=False)
dev.open()

tbl = RouteTable(dev)
tbl.get()
#tbl.get('10.13.10.0/23', protocol='static')
print tbl
for item in tbl:
    print 'protocol:', item.protocol
    print 'age:', item.age
    print 'via:', item.via
    print

dev.close()
