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
"""Project files."""
__version__ = '0.8.6'
import sys
import traceback

from PyQt5.QtWidgets import QApplication

from .merlink_cli import MainCli
from .merlink_gui import MainWindow
from merlink.merlink_gui_utils import check_for_duplicate_instance
from . import os_utils


def start():
    """Connect desktop clients to Meraki firewalls.

    Build this with './venv/bin/python3 setup.py build' from project root
    """

    # Raise exceptions for environmental requirements.
    if sys.version_info[0] < 3 or sys.version_info[1] < 5:
        raise Exception("MerLink requires Python 3.5+")
    if sys.getfilesystemencoding().lower() in ("ascii", "ansi_x3.4-1968"):
        raise Exception("MerLink requires a UTF-8 locale.")

    """Create an interface object."""
    # If there are no command line args, start GUI; otherwise CLI
    gui_application = (len(sys.argv) == 1)
    if gui_application:
        check_for_duplicate_instance()
        app = QApplication(sys.argv)  # Required Qt logic.
        interface = MainWindow()
        setup_browser(interface)
        sys.exit(app.exec_())  # Required Qt logic.
    else:
        interface = MainCli()
        setup_browser(interface)


def setup_browser(interface):
    """Set up a browser object, login with it, and create data structures."""
    # If browser is interrupted, logout so there's no hanging session.
    try:
        interface.attempt_login()
        interface.init_ui()
    except (KeyboardInterrupt, KeyError):
        print("\nAttempting to gracefully exit...", traceback.format_exc())
        has_logged_in = (interface.browser.active_org_id != 0)
        if has_logged_in:
            interface.browser.logout()
        exit(1)
