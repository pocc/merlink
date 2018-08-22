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


import os
import sys
import subprocess
import psutil


def is_duplicate_application(program_name):
    """Detect whether there are multiple processes with the same name."""
    count = 0
    for proc in psutil.process_iter():
        if proc.as_dict(attrs=['name'])['name'] == program_name:
            count += 1
        if count >= 4:
            return True
    return False


def is_online():
    """Detects whether the device is connected to the internet"""

    # Initialize vars
    result = ''
    ping_command = ''
    i = 0

    if sys.platform == 'win32':
        # -n 1 = count of 1
        # We may want to ignore a time out in case the next ping is successful
        # 300ms timeout because a 300ms+ connection is a bad connection
        ping_command = 'ping -n 1 -w 300 8.8.8.8'

    elif sys.platform == 'darwin' or sys.platform.startswith('linux'):
        # -c 1 = count of 1
        # Use smallest interval of .1s to minimize time for connectivity test
        ping_command = 'ping -c 1 -i 0.1 8.8.8.8'
    else:
        print("ERROR: Unsupported sys.platform!")

    # unreachable and failure are windows messages; 0 packets received is *nix
    while 'unreachable' not in result and 'failure' not in result and i < 4 \
            and '0 packets received' not in result:
        result = \
            subprocess.Popen(ping_command.split(), stdout=subprocess.PIPE
                             ).communicate()[0].decode('utf-8')
        i += 1

    online_status = 'unreachable' not in result and 'timed out' \
                    not in result and 'failure' not in result
    return online_status


def list_vpns():
    """This script will get the existing VPN connections from the OS."""
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


def open_vpnsettings():
    """Opens OS-specific VPN settings."""
    if sys.platform == 'win32':
        # Opens Windows 10 Settings > Network & Internet > VPN
        os.system('start ms-settings:network-vpn')
    elif sys.platform == 'darwin':
        # Opens macOS System Settings > Network
        os.system('open /System/Library/PreferencePanes/Network.prefPane/')
    elif sys.platform.startswith('linux'):  # covers vaild 'linux', 'linux2'
        # Opens System Settings > Network
        os.system('nm-connections-editor')


def pyinstaller_path(relative_path):
    """When using the --onefile flag, PyInstaller will by default extract
    necessary files into a temporary folder named '_MEIPASS2'. In order for
    the executable to access them, file paths must be modified to include
    this folder name.

    Executables using --onedir are not affected as the files are where they are
    expected to be in the original or installation folder

    Modified form source: https://stackoverflow.com/questions/7674790"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
