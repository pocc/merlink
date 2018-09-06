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

"""Given VPN vars, uses OS built-ins to create/connect a L2TP/IPSEC VPN."""
import sys
import subprocess
from os import system

from src.modules.os_utils import pyinstaller_path


class VpnConnection:
    """
    VpnConnection list arguments
        vpn_data
            vpn_name
            psk
            ip
            ddns
            username
            password
        windows_options
            dns_suffix
            idle_disconnect_seconds
            split_tunneled
            remember_credentials
            use_winlogon
            DEBUG

    VpnConnection takes 2 lists as args: vpn_data and vpn_options
        Required VPN parameters will arrive in vpn_data
        Any OS-specific VPN parameters will go into vpn_options
    """

    def __init__(self, vpn_data):
        super(VpnConnection, self).__init__()
        print('showing')
        self.vpn_data = vpn_data
        self.vpn_name = ''
        self.vpn_uuid = ''
        platform = sys.platform
        # Numbers arbitrarily chosen
        if platform == 'win32':
            self.os_index = 0
        elif platform == 'darwin':
            self.os_index = 1
        elif platform.startswith('linux'):
            self.os_index = 2
        else:
            self.os_index = 3

    def sanitize_variables(self):
        """Sanitize variables for powershell/bash input."""
        for i in range(len(self.vpn_data)):
            # Convert to string
            self.vpn_data[i] = str(self.vpn_data[i])
            # '$' -> '`$' for powershell and '$' -> '\$' for bash
            self.vpn_data[i] = self.vpn_data[i].replace('$', '`$')
            # Surround each var with double quotes in case of spaces
            self.vpn_data[i] = '\"' + self.vpn_data[i] + '\"'

    def attempt_windows_vpn(self, vpn_options):
        """Attempt to connect to Windows VPN.

        * Arguments sent to powershell MUST BE STRINGS
        * Each argument cannot be the empty string or null or PS will think
          there's no param there!!!
        * Last 3 ps params are bools converted to ints (0/1) converted to
          strings. It's easy to force convert '0' and '1' to ints on
          powershell side.
        * Setting execution policy to unrestricted is necessary so that we
          can access VPN functions
        * Email CANNOT have spaces, but password can.
        """

        self.sanitize_variables()

        # 32bit powershell path :
        # 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        # Opinionated view that 32bit is not necessary
        powershell_path = \
            'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe'

        for i in range(len(self.vpn_options)):
            # Convert to string
            self.vpn_options[i] = str(self.vpn_options[i])

        return subprocess.call(
            [powershell_path, '-ExecutionPolicy', 'Unrestricted',
             pyinstaller_path('src\scripts\connect_windows.ps1'),
             *self.vpn_data, *self.vpn_options])
        # subprocess.Popen([], creationflags=subprocess.CREATE_NEW_CONSOLE)
        #  open ps window

    def attempt_macos_vpn(self, vpn_options):
        """Attempt to connect over VPN on macOS.

        scutil is required to add the VPN to the active set. Without this,
        it is not possible to connect, even if a VPN is listed in Network
        Services

        scutil --nc select <connection> throws '0:227: execution error: No
        service (1)'. if it's a part of the build script instead of here.
        This is why it's added directly to the osacript request.
        Connection name with forced quotes in case it has spaces.
        """

        print("Creating macOS VPN")

        self.vpn_name = self.vpn_data[0]
        scutil_string = 'scutil --nc select ' + '\'' + self.vpn_name + '\''
        print("scutil_string: " + scutil_string)
        # Create an applescript execution string so we don't
        # need to bother with parsing arguments with Popen
        command = 'do shell script \"/bin/bash src/scripts/build_macos_vpn.sh' \
                  + ' \'' + self.vpn_data[0] + '\' \'' + self.vpn_data[1] + \
                  '\' \'' + self.vpn_data[2] + '\' \'' + self.vpn_data[3] + \
                  '\' \'' + self.vpn_data[4] + '\'; ' + scutil_string + \
                  '\" with administrator privileges'
        # Applescript will prompt the user for credentials in order to create
        #  the VPN connection
        print("command being run: " + command)
        result = subprocess.Popen(['/usr/bin/osascript', '-e', command],
                                  stdout=subprocess.PIPE)

        # Get the result of VPN creation and print
        output = result.stdout.read()
        print(output.decode('utf-8'))

        # Connect to VPN.
        # Putting 'f' before a string allows you to insert vars in scope
        print("Connecting to macOS VPN")
        print("Current working directory: " + str(system('pwd')))
        return subprocess.call(
            ['bash',
             'src/scripts/connect_macos.sh',
             self.vpn_name]
        )

    def attempt_linux_vpn(self, vpn_options):
        """Attempt to connect on linux.

        * FPM executes `chmod a+x` on the merlink connect script post-install.
        * sudo required to create a connection with nmcli
        * pkexec is built into latest Fedora, Debian, Ubuntu.
        * 'pkexec <cmd>' correctly asks in GUI on Debian, Ubuntu but in
          terminal on Fedora
        * pkexec is PolicyKit, which is the preferred means of asking for
          permission on LSB
        """
        return subprocess.Popen(['pkexec', pyinstaller_path(
            'src/scripts/connect_linux.sh'), *self.vpn_data, *vpn_options])

    def disconnect(self):
        """Disconnect all connected VPNs"""
        if self.is_vpn_connected():
            linux_command = 'nmcli con down uuid '
            command_string = [
                'rasdial ' + self.vpn_name + '/disconnect',
                '',
                linux_command + self.vpn_uuid,
                '']
            subprocess.call(
                [command_string[self.os_index]],
            )

    def get_all_vpn_uuids(self):
        """Return a list of type-vpn uuids"""
        linux_command = "nmcli --fields uuid,type con show | grep vpn " \
                        "| awk '{print $1}'"
        command_string = [
            "",
            "",
            linux_command,
            ""
        ]

        command_output = subprocess.Popen(
            [command_string[self.os_index]],
            shell=True,
            stdout=subprocess.PIPE,
        ).communicate()[0]
        uuid_list = command_output.decode('utf-8').split('\n')
        return uuid_list

    def is_vpn_connected(self):
        """Detect whether any VPN is connected or not.

        WINDOWS = 0, MACOS = 1, LINUX = 2, UNKNOWN = 3
        """
        search_string = ['vpn', '', 'Connected to', '']
        vpn_command = [
            "nmcli --fields name,type con show --active | grep vpn",
            "",
            "rasdial",
            "",
        ]

        subprocess_output = subprocess.Popen(
            [vpn_command[self.os_index]],
            stdout=subprocess.PIPE
        )
        command_stdout = subprocess_output.communicate()[0].decode('utf-8')
        # if the search string is in the command stdout, there are active vpns
        return search_string[self.os_index] in command_stdout

    def get_vpn_name_by_uuid(self, uuid):
        """Get the VPN name given a UUID"""
        # Get all connections, filter by uuid, and return the 2nd field (name)
        linux_command = "nmcli --fields uuid,name con show | grep " + \
                        uuid + " | cut -d\  -f2-"

        vpn_command = [
            "",
            "",
            linux_command,
            "",
        ]

        vpn_name = subprocess.Popen(
            [vpn_command[self.os_index]],
            shell=True,
            stdout=subprocess.PIPE,
        ).communicate()[0].decode('utf-8').strip()

        return vpn_name
