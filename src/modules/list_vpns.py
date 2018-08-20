# -*- coding: utf-8 -*-
# Copyright 2018 Ross Jacobs All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script will get the existing VPN connections from the OS."""
import sys
import subprocess


def list_vpns():
    if sys.platform == 'win32':
        return subprocess.check_output(['powershell', 'get-vpnconnection'])
    if sys.platform == 'darwin':
        return subprocess.check_output(['networksetup', '-listpppoeservices'])
    if sys.platform.startswith('linux'):  # linux, linux2 are both valid
        # Get all connections, filter by type vpn, and then print as columns
        return subprocess.check_output(['nmcli -f UUID,TYPE,NAME con | '
                                        'awk \'$2 =="vpn" {print $3, $1}\' | '
                                        'column -t'],
                                       shell=True).decode('UTF-8')
