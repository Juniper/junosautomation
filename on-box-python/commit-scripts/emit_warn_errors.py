#!/usr/bin/env python
#
# Copyright (c) 1999-2018, Juniper Networks Inc.
#
# All rights reserved.
#
# Script to emit warning/error messages from commit script

import jcs


def main():
    jcs.emit_warning("Warning message from Python commit script")
    jcs.emit_error("Error message from Python commit script")

if __name__ == '__main__':
    main()