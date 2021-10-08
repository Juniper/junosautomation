from jnpr.junos import Device
from jnpr.junos.utils.config import Config

dev = Device()
dev.open()

cu = Config(dev)
data = """interfaces {
    ge-1/0/1 {
        description "MPLS interface";
        unit 0 {
            family mpls;
        }
    }
    ge-1/0/2 {
        description "MPLS interface";
        unit 0 {
            family mpls;
        }
    }
}
protocols {
    mpls {
        interface ge-1/0/1;
        interface ge-1/0/2;
    }
}
"""
cu.load(data, format='text')
cu.pdiff()
if cu.commit_check():
   cu.commit()
else:
   cu.rollback()
