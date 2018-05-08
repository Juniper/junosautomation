#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to dump op script input to a file .

from junos import Junos_Context


def main():
    # open a file
    fo = open("/var/tmp/op_input_extract.txt", "w+")

    # Write the dictionary to the file
    fo.write(str(Junos_Context))
    fo.write("\n\n")

    # Access junos-context fields
    fo.write("hostname: " + str(Junos_Context['hostname']) + "\n")
    fo.write("chassis: " + str(Junos_Context['chassis']) + "\n")
    fo.write("localtime: " + str(Junos_Context['localtime']) + "\n")
    fo.write("localtime-iso: " + str(Junos_Context['localtime-iso']) + "\n")
    fo.write("pid: " + str(Junos_Context['pid']) + "\n")
    fo.write("product: " + str(Junos_Context['product']) + "\n")
    fo.write("re-master: " + str(Junos_Context['re-master']) + "\n")
    fo.write("routing-engine-name: " + str(Junos_Context['routing-engine-name']) + "\n")
    fo.write("script-type: " + str(Junos_Context['script-type']) + "\n")
    fo.write("tty: " + str(Junos_Context['tty']) + "\n")
    fo.write("user-context: " + str(Junos_Context['user-context']) + "\n")

    # close the file
    fo.close()

if __name__ == '__main__':
    main()