from jnpr.junos import Device
from jnpr.junos.utils.config import Config

dev = Device(host='xxxx', user='demo', password='demo123', gather_facts=False)
dev.open()

cu = Config(dev)
diff = cu.diff()
if diff:
    cu.rollback()
dev.close()
