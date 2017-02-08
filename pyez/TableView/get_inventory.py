from jnpr.junos import Device
from jnpr.junos.factory.factory_loader import FactoryLoader
import yaml,sys
router_name = "xxx"

with open("table_views.yml", 'r') as tvs:
    globals().update(FactoryLoader().load(yaml.load(tvs)))
with Device(host=router_name, user='xxxxx', password='xxxx', gather_facts=False) as dev:
    inv = ChassisInventoryTable(dev)
    inv.get()
    print "Collecting hardware inventory from router and update into file inventory.csv"
    f = open("inventory.csv", 'w')
    sys.stdout = f
    for item in inv:
        print "Router Name",",","Item Name",",","Description",",","Serial Number",",","Part Number",",","Version",",","Model Number"
        print router_name,",",item.name,",",item.desc,",",item.sn
    
        for i in [item.FPM, item.FDM, item.PEM, item.RE]:
            for j in i:
                print router_name,",",j.name,",",j.desc,",",j.sn,",",j.pn,",",j.ver,",",j.model
        for k in item.FPC:
            print router_name,",",k.name,",",k.desc,",",k.sn,",",k.pn,",",k.ver,",",j.model
            for l in k.MIC:
                print router_name,",",l.name,",",l.desc,",",l.sn,",",l.pn,",",l.ver,",",j.model
                for m in l.PIC:
                    print router_name,",",m.name,",",m.desc,",",m.sn,",",m.pn
                    for n in m.PORT:
                        print router_name,",",n.name,",",n.desc,",",n.sn,",",n.pn,",",n.ver
    f.close()