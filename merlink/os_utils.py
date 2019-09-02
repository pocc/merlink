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
import datetime as dt
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
        vpninfo_cmds = ['scutil', '--nc', 'show']

        for entry in results:
            vpn_name = entry[2]
            vpn_infos = sp.check_output(vpninfo_cmds + [vpn_name], text=True)

            # Remove first line
            vpn_infos = vpn_infos.strip().split('\n', 1)[1]
            vpn_infos = vpn_infos.replace('PPP <dictionary> {', '')
            vpn_infos = vpn_infos.replace('\n  ', '\n')
            vpn_infos = vpn_infos.replace("}", "")
            connection_vpn_dict = parse_machine_readable(vpn_infos)
            server_name = connection_vpn_dict['CommRemoteAddress']
            user_name = connection_vpn_dict['AuthName']
            # Data derived from ppp.log
            ppp_data = get_macos_vpn_log_data(server_name, user_name)
            vpn_list[entry[1]] = {
                "is_connected": entry[0] == "Connected",
                "guid": entry[1],
                "name": entry[2],
                "type": entry[3],
                **connection_vpn_dict,
                **ppp_data
            }
        # At some point add 'scutil --nc status <vpn connection>'
        return vpn_list
    else:
        # Get all connections, filter by type vpn, and then print as columns
        vpn_list = sp.check_output(
            ['nmcli -f UUID,TYPE,NAME con | awk \'$2 =="vpn" '
             '{print $3, $1}\' | column -t'],
            shell=True).decode('UTF-8')

    return vpn_list


def get_macos_vpn_log_data(vpn_name, user_name) -> dict:
    """Return the last time a VPN connected using info from /var/log/ppp.log

    Searching on the basis of server name and username doesn't gaurantee that
    we get info for correct VPN connection (i.e. they do not constitute
    primary keys), but we most likely will uniquely identify VPN connection.

    Essentially: Search for server/username in 30 second chunk. If success
    within 30s, continue and get bytes in/bytes out.
    """
    result_dict = {
        "last_attempted": "Never",
        "last_connected": "Never",
        "vpn_uptime": "-",
        "bytes_sent": "-",
        "bytes_recv": "-",
    }
    flooring_offset = 60
    with open("/var/log/ppp.log") as f:
        text = f.read()
    vpn_inits = re.findall(r"(.+) : L2TP connecting to server '" + vpn_name + "'", text)
    if vpn_inits:
        server_times = re.findall(r"(.+) : L2TP connecting to server '" + vpn_name + "'", text)
        server_start_dt = dt.datetime.strptime(server_times[-1], "%a %b  %d %H:%M:%S %Y")
        result_dict["last_attempted"] = server_start_dt.isoformat().replace('T', ' ')
    else:
        return result_dict

    # Strategy for finding last connected is to find last success and work backwards 30s
    success_times = re.findall(r"(.+) : Committed PPP store on install command", text)
    # Process should take less than 30 seconds. This is an identity check.
    success_time = None
    success_server_time = None
    success_auth_time = None

    auth_times = re.findall(r"(.+) : sent \[PAP AuthReq.*? user=\"" + user_name + "\"", text)
    if not auth_times:
        return result_dict

    for timestamp in success_times:
        success_time_candidate = dt.datetime.strptime(timestamp, "%a %b  %d %H:%M:%S %Y")
        min_success_init_time = success_time_candidate - dt.timedelta(0, 30)
        for server_timestamp in server_times:
            server_time_dt = dt.datetime.strptime(server_timestamp, "%a %b  %d %H:%M:%S %Y")
            if success_time_candidate > server_time_dt > min_success_init_time:
                success_server_time = server_time_dt
        for auth_timestamp in auth_times:
            auth_time_dt = dt.datetime.strptime(auth_timestamp, "%a %b  %d %H:%M:%S %Y")
            if success_time_candidate > auth_time_dt > min_success_init_time:
                success_auth_time = auth_time_dt
        # If there's a matching preceding server/username in the last 30s, treat as same connection
        if success_server_time and success_auth_time:
            success_time = success_time_candidate

    if success_time:
        result_dict["last_connected"] = success_time.isoformat().replace('T', ' ')
        # Find bytes received/sent whose minutes log is +60s (flooring_offset) to this connection
        minutes = re.findall(r"(.+) : Connect time ([\d.]+) minutes.", text)
        expected_connection_max = None
        for timestamp_str, connection_uptime_str in minutes:
            connection_uptime_ceil = int(float(connection_uptime_str))*60 + flooring_offset
            timestamp = dt.datetime.strptime(timestamp_str, "%a %b  %d %H:%M:%S %Y")
            expected_connection_max = success_time + dt.timedelta(0, connection_uptime_ceil)
            if expected_connection_max > timestamp > success_time:
                result_dict["vpn_uptime"] = str(float(connection_uptime_str)) + ' min'

        if result_dict["vpn_uptime"] != '-' and expected_connection_max:
            txrx = re.findall(r"(.+) : Sent (\d+) bytes, received (\d+) bytes.", text)
            for timestamp, bytes_sent, bytes_recv in txrx:
                timestamp = dt.datetime.strptime(timestamp, "%a %b  %d %H:%M:%S %Y")
                if expected_connection_max > timestamp > success_time:
                    result_dict["bytes_sent"] = bytes_sent + 'B'
                    result_dict["bytes_recv"] = bytes_recv + 'B'

    return result_dict


def parse_machine_readable(text):
    """Many programs produce "machine readable" output which consists of
    key:value pairs separated by : and delimited by \n.
    Return a dict of that text
    """
    result_dict = {}
    for line in text.strip().split('\n'):
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
