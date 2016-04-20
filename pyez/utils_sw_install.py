from jnpr.junos import Device
from jnpr.junos.utils.sw import SW

dev = Device(host='xxxx', user='demo', password='demo123', gather_facts=False)
dev.open()

def update_progress(dev, report):
    print dev.hostname, '> ', report

sw = SW(dev)
ok = sw.install(package=r'/Users/nitinkr/Downloads/jinstall-1x.1xxxx.tgz', progress=update_progress)
# progress takes boolean values too from 1.2.3 version onwards
#ok = sw.install(package=r'/Users/nitinkr/Downloads/jinstall-1x.1xxxx.tgz', progress=True)
if ok:
    print 'rebooting'
    sw.reboot()
