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

"""This is the MVC controller for both gui and cli interfaces"""
import sys
from PyQt5.QtWidgets import QApplication

# Local modules
from src.gui.main_window import MainWindow
from src.gui.login_dialog import LoginDialog
from src.cli.merlink_cli import MainCli


class Controller:
    """This is the MVC controller for both gui and cli interfaces.

    This class will be called by /merlink.py and will control the application.
    Controller uses an interface object whose methods are implemented by
    both MainWindow and MainCli.

    Attributes:
        interface (MainWindow | MainCli): Calls interface-dependent functions
          (this is a primitive form of overloading).
        app (QApplication): Required for the Qt program flow, not used for CLI

    """
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self):
        super(Controller, self).__init__()

        # If there is one argument, start GUI
        # Otherwise, start CLI
        gui_application = (len(sys.argv) == 1)
        if gui_application:
            self.app = QApplication(sys.argv)
            # We want to be able to be connected with VPN with systray icon
            self.app.setQuitOnLastWindowClosed(False)
            self.interface = MainWindow()
            # Make main window grayed out while user logs in
            self.interface.setEnabled(False)
            login = LoginDialog()
            login.exec_()
            # Assuming that if this executes properly, we'll have a
            # browser from the login fn that has the required cookies
            self.interface.browser = login.browser
            # Make main window active again
            self.interface.setEnabled(True)

        else:
            # MainCli After 'Main Window' convention
            self.interface = MainCli()
            exit()

        self.program_structure()
        if gui_application:
            # Required Qt logic to start window
            self.app.exec_()

        sys.exit()

    def program_structure(self):
        """Contains the interface-independent structure of the program.

        Currently, it implements a couple functions that start the
        GUI application while the CLI is still unwritten.

        Main menu should show the following across interfaces:
        1. Existing VPN connections that we can connect to
        2. After list of VPN connections, have a "+ Add a connection" option
        3. Indicate which VPN connections that are currently active (if any)
        4. Route table (should change when a VPN connection is made)
        5. Latency/loss/bandwidth graph used for a connected VPN

        It should return the next user action
        """

        # Get organization info so we have something to show user
        self.interface.browser.scrape_initial_org_info()
        self.interface.show_main_menu()

        """
        TODO: Uncomment this section or delete
        user_action = self.interface.get_user_action()
        # Default right now is to combine them
        if user_action == 'add vpn' or user_action == 'connect vpn':
            self.interface.add_vpn()
            self.interface.connect_vpn()
            self.interface.show_result()
        elif user_action == 'troubleshoot vpn':
            self.interface.troubleshoot_vpn()
        elif user_action == 'quit':
            exit()
        """