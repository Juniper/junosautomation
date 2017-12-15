#!/usr/bin/env python
#
# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License, which is located at
# http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by the parties, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied.
#
# Author.........: Diogo Montagner <dmontagner@juniper.net>
# Created on.....: 15/Dec/2017
# Version........: 1.0
# Platform.......: agnostic
# Description....: Simple example of utilising PyEZ tables (part of bb3 example)
#

from jnpr.junos.factory import loadyaml
from os.path import splitext
_YAML_ = splitext(__file__)[0] + '.yml'
globals().update(loadyaml(_YAML_))
