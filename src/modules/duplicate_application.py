#!/usr/bin/python3
import psutil
import sys
from .modal_dialogs import error_dialog

# For some reason, merlink creates 2 processes.
# If we have 4 processes, that means that there have been 2 instances launched.
# Thus, this is the 2nd process and this function will return True to kill it.


def is_duplicate_application():
    count = 0
    for proc in psutil.process_iter():
        if proc.as_dict(attrs=['name'])['name'] == 'merlink':
            count += 1
        if count >= 4:
            return True
    return False
