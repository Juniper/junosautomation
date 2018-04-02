#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to deal with command line arguments

import argparse

# Define arguments dictionary
arguments = {'arg1': 'value1', 'arg2': 'value2'}


def main():
    parser = argparse.ArgumentParser(description='This is a demo script.')

    parser.add_argument('-arg1', required=True)
    parser.add_argument('-arg2', required=True)

    args = parser.parse_args()

    print args.arg1
    print args.arg2

if __name__ == '__main__':
    main()
