from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos import Device
from jnpr.junos.utils.scp import SCP

dev = Device(host='xxxx', user='demo', password='demo123')
dev.open()

ss = StartShell(dev)
ss.open()
ss.run('cli -c "request support information | save /var/tmp/information.txt"')
with SCP(dev) as scp:
    scp.get('/var/tmp/information.txt', 'info.txt')

ss.close()