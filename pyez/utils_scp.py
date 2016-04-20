from jnpr.junos import Device
from jnpr.junos.utils.scp import SCP

dev = Device(host='xxxx', user='demo', password='demo123')
dev.open()

with SCP(dev, progress=True) as scp:
     scp.get('/var/tmp/nitin.log','info.txt')
dev.close()
