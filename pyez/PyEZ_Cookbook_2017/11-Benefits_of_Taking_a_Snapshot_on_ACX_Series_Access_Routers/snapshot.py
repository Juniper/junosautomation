# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.fs import FS
from jnpr.junos.rpcmeta import _RpcMetaExec
from jnpr.junos.exception import *
from lxml import etree
from pprint import pprint
import re
import os
import errno
import os.path
import time
import sys
import socket

# variables #

if len(sys.argv) > 2:
    print("Please only call me with one parameter")
    sys.exit()

device_ip = sys.argv[1]

try:
    socket.inet_aton(device_ip)
except Exception as err:
    print err
    sys.exit(1)

path = "/home/idelrio/scripts/snapshoter/"
disable_cmds = path + "disable_cmds.txt"
enable_syslog = path + "enable_syslog.txt"
filename_snap = path + "files/" + device_ip + ".snap"
filerun = path + device_ip + ".run"
filelog = path + "/log/" + device_ip + "_" + \
    time.strftime("%Y-%m-%d_%H:%M:%S") + ".log"

# functions #


def close():

    file_log.close()
    os.remove(filename_snap)
    os.remove(filerun)
    j_device.close()


def log(text):

    file_log.write(text)


def my_commit(file_path, device):

    # load snippet configuration
    cfg = Config(device)

    # lock candidate configuration
    cfg.lock()

    # load configuration
    try:
        cfg.load(path=file_path, format="set", merge=True, ignore_warning=True)
    except ConfigLoadError as e:
        if e.rpc_error['severity'] == 'warning':
            pass
        else:
            raise

    # commit configuration
    if cfg.commit():
        pass
    else:
        print "Failed to commit configuration.Aborting!"
        log("Failed to commit configuration.Aborting!")
        close()
        sys.exit(1)

    # unlock configuration
    cfg.unlock()


# BEGIN #

# open log file #

file_log = open(filelog, "w")

print ""
print "##########################"
print "### Auto-snapshot v1.0 ###"
print "##########################"
print ""

# Is there any process that is targeting the same device already running? #

if os.path.exists(filerun):
    print "-> There is another script instance on same device", device_ip
    log("-> There is another script instance on same device")
    file_log.close()
    sys.exit(1)

print "-> Connecting to ", device_ip

j_device = Device(host=device_ip, user='user', password='pass')

try:
    j_device.open()
except Exception as err:
    print "Cannot connect to device:", err
    close()
    sys.exit(1)

# increases device connection timeout #

j_device.timeout = 600

# Is the device platform ACX1100 ACX2200 ACX2200 ? #

if j_device.facts['model'] == "ACX2200" \
        or j_device.facts['model'] == "ACX1100" \
        or j_device.facts['model'] == "ACX2100":
    print "-> Device platform: ", j_device.facts['model']
else:
    print "-> (i) Platform device is not ACX1100/ACX2100/ACX2200"
    log("-> (i) Platform device is neither ACX1100 nor ACX2200 or ACX2100")
    close()
    sys.exit(1)


# Inform other scripts what device is the script targeting into. #

frun = open(filerun, "w")

# Looks for input/output errors from previous snapshot #

text_file_snap = open(filename_snap, "w")
op = j_device.rpc.file_show(filename='/var/log/snapshot')
text_file_snap.write(etree.tostring(op))
text_file_snap.close()

with open(filename_snap) as f:
    for line in f:
        if re.search('Input/output error', line):
            print "-> (e) Device has Input/output error.Aborting snapshot!"
            log("-> (e) Device has Input/output error.Aborting snapshot!")
            close()
            sys.exit(1)

text_file_snap.close()

# request system storage cleanup #

print "-> Performing system storage cleanup, please be patient"

fs = FS(j_device)
fs.storage_cleanup()

# Disables traceoptions + syslog #

print "-> Disabling syslog + traceoptions (when enabled)"
my_commit(disable_cmds, j_device)

# Take a snapshot #

print "-> Snapshoting the device.."

try:
    rsp = j_device.rpc.request_snapshot(slice='alternate', dev_timeout=600)
except Exception as err:
    print "--> (e) Error when snapshoting the device!", err
    log("--> (e) Error when snapshoting the device!")


# enables syslog + keep traceoptions disabled #

print "-> Re-enabling only syslog!"
my_commit(enable_syslog, j_device)

# shows contents of dumpdates file #

dumpd_file = j_device.rpc.file_show(filename='/etc/dumpdates')
dumpf = etree.tostring(dumpd_file, encoding='utf8', method='text')
print ""
print "		[Content of /etc/dumpdates]"
print dumpf
print "-> The End"
log(dumpf)

# close #

close()
