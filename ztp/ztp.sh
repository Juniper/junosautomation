#!/bin/sh
#
# Copyright (c) 1999-2017, Juniper Networks Inc.
#
# All rights reserved.
#
#

CLI=/usr/sbin/cli
FETCH=/usr/bin/fetch-secure

WORK_DIR=/var/tmp/ztp/
CONFIG=$WORK_DIR/base_config.conf
CONFIG_SAVED=$WORK_DIR/save.base_config.conf

PING_SERVER=10.0.0.1  # Test Server IP

SERVER_IP=10.0.0.1    # Server IP
SERVER_USER=username
SERVER_PASS=password
SRC_CONFIG=/var/ftp/base_config.conf

if [ ! -d $WORK_DIR ]; then
    /bin/mkdir -p $WORK_DIR || exit 1
fi

fetch_file()
{
    src=$1
    dest=${2:--}
    $FETCH -o $dest ftp://$SERVER_USER:$SERVER_PASS@$SERVER_IP/$src 2>/dev/null
}

say()
{
    echo $*
}

pass()
{
    say "PASS: " $*    
}

fail()
{
    say "FAIL: " $*    
}
set -x
#Verify that OS image upgraded through ZTP is proper one 
EXPECT_JUNOS_VER=`fetch_file /etc/dhcpd.conf | sed -n '/image-file-name.*tgz/s/.*x86-..-\([^-]*\).*/\1/p'`
ACTUAL_JUNOS_VER=`sed 's/-.*//' /packages/sets/active/junos-release`

if [ ${EXPECT_JUNOS_VER:-0} = ${ACTUAL_JUNOS_VER:-1} ]; then
    pass "Junos image upgraded through ZTP is proper"
else
    fail "Junos image upgraded through ZTP is not proper" 
    #exit
fi

# Download Configuration file from TFTP server, Apply configuration and commit
fetch_file $SRC_CONFIG $CONFIG
mgd commit $CONFIG

# Validate connections and services  
cli_output=`$CLI <<!
ping $PING_SERVER count 4
!`

if echo "$cli_output" | grep -q "0% packet loss"; then
    pass "End to End Validation"
else
    fail "End to End Validation"
fi

#Take router configuration backup and upload to backup server  
cli_output=`$CLI 2>&1 <<!
configure
save $CONFIG_SAVED
!`
uploaded_bytes=`$CLI -c "file copy $CONFIG_SAVED ftp://$SERVER_USER:$SERVER_PASS@$SERVER_IP//tmp/" 2>&1 | awk '{print $2}'`
actual_bytes=`ls -l $CONFIG_SAVED | awk '{print $5}'`
if [ ${uploaded_bytes:-0} -eq ${actual_bytes:-1} ]; then
    pass "Configuration Backup"
else
    fail "Configuration Backup"
fi

# Update Site data base in NMS and Site registration in BSS
host=`hostname`
NMS_DB=$WORK_DIR/nms_database.$host
echo "$host:$ACTUAL_JUNOS_VER" >$NMS_DB
uploaded_bytes=`$CLI -c "file copy $NMS_DB ftp://$SERVER_USER:$SERVER_PASS@$SERVER_IP//tmp/" 2>&1 | awk '{print $2}'`
actual_bytes=`ls -l $NMS_DB | awk '{print $5}'`
if [ ${uploaded_bytes:-0} -eq ${actual_bytes:-1} ]; then
    pass "NMS Database Update"
else
    fail "NMS Dtaabase Update"
fi
