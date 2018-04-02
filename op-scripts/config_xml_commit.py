#!/usr/bin/python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#

# Script to commit configuration using 'xml' format using PyEZ.

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import LockError, CommitError, UnlockError, ConfigLoadError
import jcs

dev = Device()
dev.open()
config_xml = """
    <configuration>
        <system>
            <scripts>
                <op>
                    <file>
                        <name>demo.py</name>
                    </file>
                </op>
            </scripts>
        </system>
    </configuration>
"""
cu = Config(dev)
try:
    cu.lock()
    cu.load(config_xml, format="xml", merge=True)
    cu.commit()
    cu.unlock()

# Catch configuration lock error
except LockError:
    jcs.syslog("external.error,  Unable to lock configuration")
    dev.close()

except ConfigLoadError:
    jcs.syslog("external.error,  Unable to load configuration")
    cu.unlock()

except CommitError:
    jcs.syslog("external.error, Unable to commit configuration")
    cu.unlock()

except UnlockError:
    jcs.syslog("external.error,Unable to unlock configuration")
    dev.close()