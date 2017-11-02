#!/usr/bin/python

# purpose is to check the rsvp interface reservation on an ACX device

import os
import sys
import yaml
import glob
import errno
from pprint import pprint
from jnpr.junos import Device
from jnpr.junos.factory.factory_loader import FactoryLoader
from jnpr.junos.op.ethport import EthPortTable
from jnpr.junos.rpcmeta import _RpcMetaExec
from lxml import etree

# U&P
_uname = "user"
_upass = "pass"

# YAML table for RSVP
RSVP_INT_yml = '''
---
Rsvp_int_Table:
 rpc: get-rsvp-interface-information
 item: rsvp-interface
 key: interface-name
 view: RsvpIntView
RsvpIntView:
 fields:
  interface_name: interface-name
  rsvp_status: rsvp-status
  rsvp_telink_active_reservation: rsvp-telink/active-reservation
  rsvp_telink_subscription: rsvp-telink/subscription
  rsvp_telink_available_bandwidth: rsvp-telink/available-bandwidth
  rsvp_telink_total_reserved_bandwidth: rsvp-telink/total-reserved-bandwidth
  rsvp_telink_high_watermark: rsvp-telink/high-watermark
'''

globals().update(FactoryLoader().load(yaml.load(RSVP_INT_yml)))

# Setup Output File

_rsvpout = "/var/tmp/rsvp.out"


def log(text):

    file_log.write(text)


file_log = open(_rsvpout, "w")


def get_rsvp(_IP1):
    try:
        _dev = Device(host=_IP1, user=_uname, password=_upass)
        _dev.open()
    except Exception as err:
        print "Can not Connect" + _IP1, err
        return
        sys.exit(1)

    rsvp_int_T = Rsvp_int_Table(_dev)
    rsvp_int_T.get()
    for rsvp in rsvp_int_T:
        file_log.write(
            _IP1 +
            ";" +
            rsvp.interface_name +
            ";" +
            rsvp.rsvp_status +
            ";" +
            rsvp.rsvp_telink_active_reservation +
            ";" +
            rsvp.rsvp_telink_subscription +
            ";" +
            rsvp.rsvp_telink_available_bandwidth +
            '\n')

    _dev.close()


_directory = os.path.normpath("/PATH/TO/FILE/")

for subdir, dirs, files in os.walk(_directory):
    for file in files:
        if file.endswith(".txt"):
            with open(os.path.join(subdir, file), 'r') as _IP1:
                for line in _IP1:
                    line = line.strip()
                    get_rsvp(line)
