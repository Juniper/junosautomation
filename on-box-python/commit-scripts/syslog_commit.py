from junos import Junos_Configuration
import jcs

def main():
    root = Junos_Configuration
    for element in root.xpath("./snmp/community"):
        if element.find("authorization") is None or \
           element.find("authorization").text != 'read-write':
            jcs.syslog("172", "SNMP community does not have read-write access: "
                +  element.find('name').text)

if __name__ == '__main__':
    main()
