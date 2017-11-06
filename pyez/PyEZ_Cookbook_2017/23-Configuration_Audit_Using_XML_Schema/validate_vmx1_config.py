# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved
#!/opt/local/bin/python
                                                                                
import lxml                                                                     
from lxml import etree
import sys                                                         
import StringIO
import yaml
from jnpr.junos import Device
from jinja2 import Environment, FileSystemLoader, Template
import pprint
import logging


# setting logging capabilities
log = logging.getLogger() # 'root' Logger
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(funcName)s %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console) # prints to console.

# set the log level here
#log.setLevel(logging.INFO)
log.setLevel(logging.ERROR)



def render_l3vpn_schema(router_inventory_file, schema_template_file, vpn_name):

    ENV = Environment(loader=FileSystemLoader('./'))

    try:
        template = ENV.get_template(schema_template_file)
        log.info("template %s rendered !!!" % schema_template_file)

    except Exception as e:
        print "error: error rendering the template " + schema_template_file
        print e
        return None

    log.info("")
    log.info("printing the rendered template ...")
    log.info("")

    for vpn in router_inventory_file['services']['l3vpn']:
        if vpn['service_name'] == vpn_name:
            rendered_template = template.render(template=vpn)
            log.debug(rendered_template)
            return rendered_template

    # if got here, it means no VPN with service_name equals to vpn_name has been found
    print "error: could not find VPN %s" % vpn_name
    return None



def main():                                                                                


    router_inventory_file = "router_vmx1.yaml"
    l3vpn_schema_template = "l3vpns.xsd.j2"

    #
    # loading the router inventory data into a dictionary
    #
    try:
        inventory_file = open(router_inventory_file, "r")

    except Exception as e:
        print "error: error opening the file " + router_inventory_file
        print e
        sys.exit(-1)

    yaml_file = yaml.load(inventory_file)

    vmx1_hostname = yaml_file['infrastructure']['router_hostname']
    vmx1_mgmt = yaml_file['infrastructure']['router_mgmt_fxp0']


    #
    # collecting the router XML configuration
    #

    # temporary override
    rtUser = "lab"
    rtPassword = "lab123"

    try:
        vmx1_mgmt = '127.0.0.1'
        rtUser = "dmontagner"
        rtPassword = "diogo123"
        dev = Device(host=vmx1_mgmt, user=rtUser, password=rtPassword, port=2222, gather_facts=False)
        dev.open()
        print "\nConnection to %s established with success!" % vmx1_hostname

    except Exception as e:
        print "error: could not connect to %s" % vmx1_hostname
        print e
        sys.exit(-1)

    try:
        xmlConfig = dev.rpc.get_config()
        print "\nConfiguration collected from %s" % vmx1_hostname

    except Exception as e:
        print "error: could not collect the configuration from router %s" % vmx1_hostname
        print e
        sys.exit(-1)

    #
    # looping through each VPN in the inventory file
    #
    for vpn in yaml_file['services']['l3vpn']:

        print ""
        print "Auditing VPN %s ..." % vpn['service_name']

        #
        # rendering the schema file for this VPN 
        #
        rendered_schema_file = str(render_l3vpn_schema(yaml_file, l3vpn_schema_template, vpn['service_name']))

        if rendered_schema_file is None:
            print ""
            print "error: could not render the schema file !!!"
            print ""
            sys.exit(-1)

        #
        # creating the XML document for the rendered schema file
        #
        try:
            schemaXML = etree.fromstring(rendered_schema_file)
            log.warn("XML doc for %s created!" % l3vpn_schema_template)

        except Exception as e:
            print "could not create XML doc from XML schema file %s" % l3vpn_schema_template
            print e
            sys.exit(-1)

        #
        # creating the schema document for the rendered XML document of the schema file
        #
        try:
            schemaDoc = etree.XMLSchema(schemaXML)
            log.warn("XML schema created for vpn %s with schema file %s" % (vpn['service_name'], l3vpn_schema_template))
        except Exception as e:
            print "could not create XML schema for vpn %s based on schema file %s" % (vpn['service_name'], l3vpn_schema_template)
            print e
            sys.exit(-1)

        #
        # creating the XML parser based on the XML schema created previously
        #
        try:
            myXMLparser = etree.XMLParser(schema=schemaDoc)
            log.warn("XML parser based on rendered %s schema created!" % l3vpn_schema_template)
        except Exception as e:
            print "could not create XML parser based on routing_instance.xsd schema"
            print e
            sys.exit(-1)

        #
        # validating the L3VPNs configuration based on l3vpn service schema
        #
        log.warn("walking on xml tree for vpn %s" % vpn['service_name'])

        if (len(xmlConfig.xpath("//configuration/routing-instances/instance[name=\"" + vpn['service_name'] + "\"]")) > 0):
            
            # The VPN configuration exist in the router. Proceed with the audit.
            for rtInstance in xmlConfig.xpath("//configuration/routing-instances/instance[name=\"" + vpn['service_name'] + "\"]"):

                if (rtInstance.xpath("./name")[0].text == vpn['service_name']):
                    my_routing_instance_str = etree.tostring(rtInstance)
                    log.debug(my_routing_instance_str)

                    log.warn("Validating routing instance configuration for vpn %s against schema %s ..." % (vpn['service_name'], l3vpn_schema_template))

                    try:
                        etree.fromstring(my_routing_instance_str, myXMLparser)
                        print "    - audit results: PASS"
                        log.warn("Routing instance configuration for vpn %s validated against %s" % (vpn['service_name'], l3vpn_schema_template))
                    except etree.XMLSchemaError as e1:
                        log.warn("error: error validating routing instance %s" % vpn['service_name'])
                        print "    - audit results: FAIL"
                        print e1.message

                    except Exception as e:
                        log.warn("error validating routing instance %s" % vpn['service_name'])
                        print e

        else:
            print "\nerror: could not find vpn %s in the router %s" % (vpn['service_name'], vmx1_hostname)

if __name__ == "__main__":                                                      
    main()
