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

from PyQt5.QtWidgets import QApplication

from .merlink_cli import MainCli
from .merlink_gui import MainWindow
from . import os_utils


def start():
    """Connect desktop clients to Meraki firewalls.

    Build this with './venv/bin/python3 setup.py build' from project root
    """
    os_utils.kill_duplicate_applications('merlink')

    # If there are no command line args, start GUI; otherwise CLI
    gui_application = (len(sys.argv) == 1)
    if gui_application:
        app = QApplication(sys.argv)  # Required Qt logic.
        interface = MainWindow()
    else:
        interface = MainCli()
    # Login, set up data structures, and start the interface's UI.
    interface.attempt_login()

    try:
        interface.init_ui()
        if gui_application:
            app.exec_()  # Required Qt logic.
    except (KeyboardInterrupt, KeyError) as error:
        print("\nAttempting to gracefully exit...")
        interface.browser.logout()
        raise  # KeyboardInterrupt needs to be reraised.

    sys.exit()
