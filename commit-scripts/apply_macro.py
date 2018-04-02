#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to read apply-macro configuration and commits transient configuration

from junos import Junos_Configuration
import jcs


def main():
    # Get the configuration root object
    root = Junos_Configuration

    # Check for apply-macro configuration existence
    apply_macro_config = root.find("./routing-options/apply-macro[name='both-ribs']")

    if apply_macro_config:
        # Create configuration xml chunk
        transient_change_xml = """<routing-options><interface-routes>
                             <rib-group><inet>{0}</inet></rib-group></interface-routes>
                             <rib-groups><name>{1}</name><import-rib>{2}</import-rib>
                             <import-rib>{3}</import-rib></rib-groups></routing-options>
                             """.format("both-ribs", "both-ribs", "inet.0", "inet.2")

        # Committing 'transient' changes
        jcs.emit_change(transient_change_xml, "transient-change", "xml")

if __name__ == '__main__':
    main()