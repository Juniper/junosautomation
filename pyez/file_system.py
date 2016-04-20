from jnpr.junos.utils.fs import FS
from jnpr.junos import Device

dev = Device(host='xxxx', user='demo', password='demo123')
dev.open()

fs = FS(dev)
pprint(fs.ls('/var/tmp'))

dev.close()
