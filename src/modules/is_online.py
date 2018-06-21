#!/usr/bin/python3
import subprocess
from sys import platform


def is_online():
    # Initialize vars
    result = ''
    ping_command = ''
    i = 0

    if platform == 'win32':
        # -n 1 = count of 1
        # We may want to ignore a time out in case the next ping is successful
        # 300ms timeout because a 300ms+ connection is a bad connection
        ping_command = 'ping -n 1 -w 300 8.8.8.8'

    elif platform == 'darwin' or platform.startswith('linux'):
        # -c 1 = count of 1
        # Use smallest interval of .1s to minimize time for connectivity test
        ping_command = 'ping -c 1 -i 0.1 8.8.8.8'
    else:
        print("ERROR: Unsupported platform!")

    # unreachable and failure are windows messages; 0 packets received is *nix
    while 'unreachable' not in result and 'failure' not in result and i < 4 \
            and '0 packets received' not in result:
        result = subprocess.Popen(ping_command.split(),
                                  stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
        i += 1

    online_status = 'unreachable' not in result and 'timed out' not in result and 'failure' not in result
    return online_status
