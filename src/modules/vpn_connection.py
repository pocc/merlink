#!/usr/bin/python3

from src.modules.pyinstaller_path_helper import resource_path
import subprocess
from sys import platform
from os import system

"""
VpnConnection list arguments
    vpn_data
        vpn_name
        ddns
        psk
        username
        password
    windows_options
        dns_suffix
        idle_disconnect_seconds
        split_tunneled
        remember_credentials
        use_winlogon
        
VpnConnection takes 2 lists as args: vpn_data and vpn_options
    Required VPN parameters will arrive in vpn_data
    Any OS-specific VPN parameters will go into vpn_options 
"""


class VpnConnection:
    def __init__(self, vpn_data):
        super(VpnConnection, self).__init__()
        self.vpn_data = vpn_data
        self.vpn_options = []

    # Sanitize variables for powershell/bash input
    def sanitize_variables(self):
        for i in range(len(self.vpn_data)):
            # Convert to string
            self.vpn_data[i] = str(self.vpn_data[i])
            # '$' -> '`$' for powershell and '$' -> '\$' for bash
            self.vpn_data[i] = self.vpn_data[i].replace('$', '`$')
            # Surround each var with double quotes in case of spaces
            self.vpn_data[i] = '\"' + self.vpn_data[i] + '\"'

    def attempt_windows_vpn(self, vpn_options):
        self.sanitize_variables()

        self.vpn_options = vpn_options
        # 32bit powershell path :
        # 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
        # Opinionated view that 32bit is not necessary
        powershell_path = \
            'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe'

        for i in range(len(self.vpn_options)):
            # Convert to string
            self.vpn_options[i] = str(self.vpn_options[i])

        # Arguments sent to powershell MUST BE STRINGS
        # Each argument cannot be the empty string or null or PS will think
        # there's no param there!!!
        # Last 3 ps params are bools converted to ints (0/1) converted to
        # strings. It's easy to force convert
        # '0' and '1' to ints on powershell side
        # Setting execution policy to unrestricted is necessary so that we
        # can access VPN functions
        # Email CANNOT have spaces, but password can.
        return subprocess.call(
            [powershell_path, '-ExecutionPolicy', 'Unrestricted',
             resource_path('src\scripts\connect_windows.ps1'), *self.vpn_data,
             *self.vpn_options])
        # subprocess.Popen([], creationflags=subprocess.CREATE_NEW_CONSOLE)
        #  open ps window

    def attempt_macos_vpn(self, vpn_options):
        self.vpn_options = vpn_options
        print("Creating macOS VPN")
        # scutil is required to add the VPN to the active set. Without this,
        # it is not possible to connect, even if a VPN is listed in Network
        # Services
        # scutil --nc select <connection> throws '0:227: execution error: No
        # service (1)'. if it's a part of the build script instead of here.
        # This is why it's added directly to the osacript request.
        # Connection name with forced quotes in case it has spaces.

        vpn_name = self.vpn_data[0]
        scutil_string = 'scutil --nc select ' + '\'' + vpn_name + '\''
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
             vpn_name]
        )

    def attempt_linux_vpn(self, vpn_options):
        self.vpn_options = vpn_options
        """
        sudo required to create a connection with nmcli
        pkexec is built into latest Fedora, Debian, Ubuntu.
        'pkexec <cmd>' correctly asks in GUI on Debian, Ubuntu but in 
        terminal on Fedora
        pkexec is PolicyKit, which is the preferred means of asking for 
        permission on LSB
        """
        # set execution bit on bash script
        system('chmod a+x ' + resource_path('src/scripts/connect_linux.sh'))
        return subprocess.Popen(['pkexec', resource_path(
            'src/scripts/connect_linux.sh'), *self.vpn_data])
