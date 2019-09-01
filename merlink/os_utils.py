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
"""OS utilities, most of which are VPN-related."""
import os
import re
import sys
import subprocess as sp

import requests


def is_online():
    """Detect whether the device is able to connect to Meraki's website."""
    host = 'https://meraki.com'
    try:
        requests.get(host)
        return True
    except requests.exceptions.ConnectionError:
        return False


def list_vpns():
    """List the existing VPN connections from the OS.
    {"UUID": {dict data}, ...}
    """
    vpn_list = {}
    if sys.platform == 'win32':
        connections_text = sp.check_output(
            ['powershell', 'get-vpnconnection'])
        connections_text_list = connections_text.split('\n\n')
        # Make a dict out of colon-delimited output
        for connection in connections_text_list:
            connection_dict = parse_machine_readable(connection)
            # 1 to -1 to remove { and } from uuid text
            connection_dict['Guid'] = connection_dict['Guid'][1:-1]
            vpn_list[connection_dict['Guid']] = connection_dict
        return vpn_list

    elif sys.platform == 'darwin':
        scutil_output = sp.check_output(['scutil', '--nc', 'list'], text=True)
        # Capture groups (4): Connected?, GUID, Name, Interface Type
        vpn_regex = re.compile(r"\* \(([^)]+)\)\s+([0-9a-fA-F-]+)"
                               r".+?\"([^\"]*)\"\s+\[([^\]]*)\]")
        results = re.findall(vpn_regex, scutil_output)
        vpn_list = []
        vpninfo_cmds = ['scutil', '--nc', 'show']
        for entry in results:
            vpn_list[entry[1]] = {
                "is_connected": entry[0],
                "guid": entry[1],
                "name": entry[2],
                "type": entry[3],
            }
            vpn_infos = sp.check_output(vpninfo_cmds + [entry[2]], text=True)
            # Remove first line
            vpn_infos = vpn_infos.strip().split('\n', 1)[1]
            vpn_infos = vpn_infos.replace('PPP <dictionary> {', '')
            vpn_infos = vpn_infos.replace("}", "")
            vpn_list = {**vpn_list, **parse_machine_readable(vpn_infos)}
        # At some point add 'scutil --nc status <vpn connection>'
        return vpn_list
    else:
        # Get all connections, filter by type vpn, and then print as columns
        vpn_list = sp.check_output(
            ['nmcli -f UUID,TYPE,NAME con | awk \'$2 =="vpn" '
             '{print $3, $1}\' | column -t'],
            shell=True).decode('UTF-8')

    return vpn_list


def parse_machine_readable(text):
    """Many programs produce "machine readable" output which consists of
    key:value pairs separated by : and delimited by \n.
    Return a dict of that text
    """
    result_dict = {}
    for line in text.split('\n'):
        key, value = re.sub(r"\s+:\s+", ":", line).split(':')
        if value.isdigit():
            value = int(value)
        result_dict = {**result_dict, key: value}
    return dict(result_dict)


def open_vpnsettings():
    """Open OS-specific VPN settings."""
    if sys.platform == 'win32':
        # Opens Windows 10 Settings > Network & Internet > VPN
        os.system('start ms-settings:network-vpn')
    elif sys.platform == 'darwin':
        # Opens macOS System Settings > Network
        os.system('open /System/Library/PreferencePanes/Network.prefPane/')
    elif sys.platform.startswith('linux'):  # covers vaild 'linux', 'linux2'
        # Opens System Settings > Network
        sp.Popen(['nm-connections-editor'])


def pyinstaller_path(relative_path):
    """Modify the path so that assets can be found in PyInstaller's onefile.

    When using the --onefile flag, PyInstaller will by default extract
    necessary files into a temporary folder named '_MEIPASS2'. In order for
    the executable to access them, file paths must be modified to include
    this folder name.

    Executables using --onedir are not affected as the files are where they are
    expected to be in the original or installation folder

    Modified from source: https://stackoverflow.com/questions/7674790
    """
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = os.environ.get("_MEIPASS2", os.path.abspath("."))
    return os.path.join(base_path, relative_path)
