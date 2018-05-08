#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# python version of disable-interface.slax
# https://github.com/Juniper/junoscriptorium/blob/master/library/juniper/op/interfaces/disable-interface/disable-interface.slax
#

import jcs

arguments = {
  'interface': 'Interface to deactivate',
  'silent': 'Decides where the output will go, 0 -> stdout, 1 -> syslog',
  'disalbe': 'The action to be taken, "disable" by default, or "enable" '
  }


def emit_info(message,silent):
    if silent:
        jcs.syslog("user.info", message)
    else:
        print message

def emit_error(message,silent):
    if silent:
        jcs.syslog("user.error", message)
    else:
        print message


#
# execute commit
# input:
#   Device
#   configuration string
#   optional, the format of the configuration string ("xml", "txt", or "set")
# output:
#   result of load-configuration
def do_commit(dev, config_str, format="xml"):
  from jnpr.junos.utils.config import Config
  jcs.trace("do_commit() with config_str = %s" % config_str)
  cu = Config(dev)
  cu.lock()
  res = cu.load(config_str, format=format, merge=True)
  cu.commit()
  cu.unlock()
  return res

# 
# return dictionary for a given xpath element
# input:
#   xpath element
# return:
#   (tag, dict)
def recursive_dict(element):
     return element.tag, dict(map(recursive_dict, element)) or element.text

def main():
  import argparse, os, sys
  from jnpr.junos import Device

  # set script name for logging purpose
  script_name =  os.path.basename(__file__)

  # parse arguments
  parser = argparse.ArgumentParser(description='This is a demo script.')
  parser.add_argument('-interface', required=True)
  parser.add_argument('-silent', required=False, default=None)
  parser.add_argument('-disable', required=False, default="'disable'")
  args = parser.parse_args()
  interface=args.interface[1:-1] # workaround against a bug
  silent=args.silent
  disable=args.disable[1:-1] # workaround against a bug
  
  emit_info( "{:s} interface {:s} silent {:s} disable {:s}".format(script_name, interface, silent, disable), silent)
  
  dev = Device().open()
  # exit if Device open fails
  if(not dev):
    emit_error("{:s} Not able to connect to local mgd".format(script_name),silent)
    sys.exit(1)
  # compose set command
  config_set = "set interfaces {:s} {:s}".format(interface, disable)
  
  # execute while capturing exception/error
  from jnpr.junos.exception import RpcError
  res = None
  try:
    res = do_commit(dev,config_set,"set")
  except RpcError as e:
    tag, tagval = recursive_dict(e.errs[0])
    emit_error("{:s}: {:s}, {:s}".format(script_name, tag, tagval), silent)
  except:
    emit_error("{:s}: Exception {:s}".format(script_name, sys.exc_info()[0]), silent)
  else:
    emit_info("{:s}: Successfully {:s}d the interface".format(script_name,disable), silent)
    
  dev.close()

if __name__ == '__main__':
  main()