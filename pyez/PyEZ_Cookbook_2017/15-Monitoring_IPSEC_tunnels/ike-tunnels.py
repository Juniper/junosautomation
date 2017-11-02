from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from lxml import etree
import dill
import xmltodict
from io import StringIO
from contextlib import redirect_stdout
from collections import defaultdict
from operator import itemgetter

host = '172.27.75.5'
user = "root"
passwd = "root123"


def main():
    dev = Device(host=host, user=user, passwd=passwd)
    # open a connection with the device and start a NETCONF session
    try:
        dev.open()
        dev.timeout = 300
    except Exception as err:
        print("Cannot connect to device:", err)
        return
    ikepeers = dev.rpc.get_ike_security_associations_information(detail=True)
    ipsecpeers = dev.rpc.get_security_associations_information(detail=True)
    iketree = etree.ElementTree(ikepeers)
    ipsectree = etree.ElementTree(ipsecpeers)
    ikeroot = iketree.getroot()
    ipsecroot = ipsectree.getroot()
    ikeactions = iketree.findall('.//ike-security-associations-block')
    ikeparsed = [{field.tag: field.text for field in action}
                 for action in ikeactions]
    ipsecactions = ipsectree.findall('.//ipsec-security-associations-block')
    ipsecparsed = [{field.tag: field.text for field in action}
                   for action in ipsecactions]
    d = defaultdict(dict)
    for elem in ipsecparsed:
        d[elem['sa-tunnel-index']].update(elem)
    l3 = sorted(d.values(), key=itemgetter('sa-vpn-name'))
    for elem in ikeparsed:
        for elem1 in l3:
            if elem1['sa-remote-gateway'] == elem['ike-sa-remote-address']:
                elem1.update(elem)
    for idx, tunnel in enumerate(l3):
        try:
            print((idx + 1),
                  ' - ',
                  tunnel['sa-vpn-name'],
                  ' - ',
                  tunnel['sa-remote-gateway'],
                  '- ',
                  tunnel['ike-sa-index'],
                  '- ',
                  tunnel['sa-tunnel-index'],
                  ' - ',
                  "\n\t",
                  tunnel['sa-local-identity'],
                  ' - ',
                  tunnel['sa-remote-identity'],
                  '\n')
        except KeyError:
            print((idx + 1),
                  ' - ',
                  tunnel['sa-vpn-name'],
                  ' - ',
                  tunnel['sa-remote-gateway'],
                  '- ',
                  tunnel['sa-tunnel-index'],
                  ' - ',
                  '\n\t',
                  tunnel['sa-local-identity'],
                  ' - ',
                  tunnel['sa-remote-identity'],
                  '\n')
    # End the NETCONF session and close the connection
    dev.close()


main()
