"""
Sample SNMP script shows how to process object identifiers (OIDs) 
that are not supported by Junos OS on a device running Junos OS.

Load the following configuration on box:

set system scripts snmp file sample_snmp.slax oid .1.3.6.1.4.1.2636.13.61.1.9.1.1
set system scripts snmp file sample_snmp.slax oid .1.3.6.1.4.1.2636.13.61.1.9.1.1.1
set system scripts snmp file sample_snmp.slax oid .1.3.6.1.4.1.2636.13.61.1.9.1.1.1 priority 120

For making SNMP script run on-box:

set system scripts language python 
set system scripts snmp file sample_snmp.py python-script-user <user-name>

"""


import jcs

def main():

    snmp_action = jcs.get_snmp_action()
    snmp_oid = jcs.get_snmp_oid()

    jcs.syslog("8", "snmp_action = ", snmp_action, " snmp_oid = ", snmp_oid)

    if snmp_action == 'get':
        if snmp_oid == '.1.3.6.1.4.1.2636.13.61.1.9.1.1':
            jcs.emit_snmp_attributes(snmp_oid, "Integer32", "10")
        elif snmp_oid == '.1.3.6.1.4.1.2636.13.61.1.9.1.1.1':
            jcs.emit_snmp_attributes(snmp_oid, "Integer32", "211")

    elif snmp_action == 'get-next':
        if snmp_oid == '.1.3.6.1.4.1.2636.13.61.1.9.1.1':
            jcs.emit_snmp_attributes(".1.3.6.1.4.1.2636.13.61.1.9.1.1.1", "Integer32", "211")
        elif snmp_oid == '.1.3.6.1.4.1.2636.13.61.1.9.1.1.1':
            jcs.emit_snmp_attributes(".1.3.6.1.4.1.2636.13.61.1.9.1.1.2", "Integer32", "429")

if __name__ == '__main__':
    main()
