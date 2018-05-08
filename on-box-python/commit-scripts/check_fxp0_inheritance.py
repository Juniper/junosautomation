#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to emit warning if 'fxp0' configured and not inherited from 're' group.

from junos import Junos_Configuration
import jcs


def main():
    # Get configuration root object
    root = Junos_Configuration

    # Check for 'fxp0' existence
    fxp0_interface = root.find("./interfaces/interface[name='fxp0']")

    # Compare attribute value
    if fxp0_interface is not None:
        inherited_re0 = fxp0_interface.find("[@{http://xml.juniper.net/junos/*/junos}group='re0']")
        inherited_re1 = fxp0_interface.find("[@{http://xml.juniper.net/junos/*/junos}group='re1']")

        # Emit warning if 'fxp0' configured and not inheirted from 're' group
        if inherited_re0 is None and inherited_re1 is None:
            jcs.emit_warning("fxp0 configuration is present but not inherited from re group")

    else:
        jcs.emit_warning("fxp0 configuration not present")

if __name__ == '__main__':
    main()