import subprocess


def is_online():
    # Initialize vars
    result = ''
    i = 0

    # We may want to ignore a time out in case the next ping is successful
    # 300ms timeout because a 300ms+ connection is a bad connection
    while 'unreachable' not in result and 'failure' not in result and i < 4:
        result = subprocess.Popen(['ping', '-n', '1', '-w', '300', '8.8.8.8'],
                                  stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
        i += 1

    online_status = 'unreachable' not in result and 'timed out' not in result and 'failure' not in result
    return online_status