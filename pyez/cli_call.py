from jnpr.junos import Device

dev = Device(host='xxxx', user='demo', password='demo123', gather_facts=False)
dev.open()

print dev.cli("show version", warning=False)

dev.close()
