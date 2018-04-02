#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# python translation from 
# https://github.com/Juniper/junoscriptorium/blob/master/library/juniper/op/interfaces/expand-interface-port-range/expand-interface-port-range.slax
#
# example:
#   op expand_interface_port_range.py command "set interfaces ge-0/0/0-20 unit 0 family ethernet-switching vlan members data" | save /var/tmp/out
#
#

import re

arguments = { "command": "Interface set command with range" }

def main():
  import argparse, os, sys
  from jnpr.junos import Device

  # set script name for logging purpose
  script_name =  os.path.basename(__file__)

  # parse arguments
  parser = argparse.ArgumentParser(description='This is a demo script.')
  parser.add_argument('-command', required=True)
  args = parser.parse_args()
  command=args.command[1:-1] # workaround against a bug

  m = re.match("(?P<initial_command>.* [a-z][a-z]{1,2}-[0-9]+/[0-9]+/)(?P<start_port>[0-9]+)-(?P<end_port>[0-9]+)(?P<final_command>.*)",command)
  initial_command=m.group('initial_command')
  start_port=int(m.group('start_port'))
  end_port=int(m.group('end_port'))
  final_command=m.group('final_command')
  for i in range(start_port,end_port+1):
    print "{:s}{:d}{:s}".format(initial_command,i,final_command)

if __name__ == '__main__':
  main()