# This script will get the existing VPN connections from the OS

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
