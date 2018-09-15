# -*- coding: utf-8 -*-
"""Project files."""
__version__ = '0.8.6'
import sys

from PyQt5.QtWidgets import QApplication

from . import main_window as gui
from . import main_cli as cli
from . import os_utils


def run():
    """Connect desktop clients to Meraki firewalls.

    Build this with './venv/bin/python3 setup.py build' from project root
    """
    os_utils.kill_duplicate_applications('merlink')

    # If there are no command line args, start GUI; otherwise CLI
    gui_application = (len(sys.argv) == 1)
    if gui_application:
        app = QApplication(sys.argv)  # Required Qt logic.
        interface = gui.MainWindow()
    else:
        interface = cli.MainCli()

    # Login, set up data structures, and start the interface's UI.
    interface.attempt_login()
    interface.browser.org_data_setup()
    interface.init_ui()

    if gui_application:
        app.exec_()  # Required Qt logic.
    sys.exit()
