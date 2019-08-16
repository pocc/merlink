# -*- coding: utf-8 -*-
"""GUI utilities not tied to the main application object."""
import os
import signal
import psutil
import tempfile


def check_for_duplicate_instance():
    """Abort if existing application found.
    This is for GUI instances where the window might be minimized.
    No ill effects should come from killing existing process.
    """
    pid = str(os.getpid())
    pidfile = tempfile.gettempdir() + "/merlink.pid"
    if os.path.isfile(pidfile):
        with open(pidfile) as f:
            previous_pid = f.read()
        # If the pidfile contents are non-numeric, just create a new process
        if previous_pid.isdigit() and previous_pid in psutil.pids():
            print("Killing existing Merlink at PID " + previous_pid)
            os.kill(int(previous_pid), signal.SIGTERM)
    with open(pidfile, 'w') as f:
        f.write(pid)
