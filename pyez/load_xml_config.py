from jnpr.junos import Device
from jnpr.junos.utils.config import Config

dev = Device(host='xxxx', user='demo', password='demo123', gather_facts=False)
dev.open()

cu = Config(dev)
data = """<policy-options>
          <policy-statement action="delete">
            <name>F5-in</name>
            <term>
                <name>test</name>
                <then>
                    <accept/>
                </then>
            </term>
            <from>
                <protocol>mpls</protocol>
            </from>
        </policy-statement>
        </policy-options>"""


cu.load(data)
if cu.commit_check():
   cu.commit()
else:
   cu.rollback()
