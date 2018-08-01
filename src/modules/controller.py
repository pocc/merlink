#!/usr/bin/python

#  Python libraries
import sys
from PyQt5.QtWidgets import QApplication

# Local modules
from src.gui.main_window import MainWindow
from src.gui.login_dialog import LoginDialog
from src.gui.modal_dialogs import show_error_dialog, show_question_dialog, \
    show_feature_in_development_dialog
from src.cli.merlink_cli import MainCli


class Controller:
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self):
        super(Controller, self).__init__()

        # If there is one argument, start GUI
        # Otherwise, start CLI
        self.gui_application = (len(sys.argv) == 1)
        if self.gui_application:
            self.app = QApplication(sys.argv)
            # We want to be able to be connected with VPN with systray icon
            self.app.setQuitOnLastWindowClosed(False)
            self.interface = MainWindow()
            self.login = LoginDialog()
            self.login.exec_()
            # Assuming that if this executes properly, we'll have a
            # browser from the login fn that has the required cookies
            self.interface.browser = self.login.browser

        else:
            self.interface = MainCli()  # After 'Main Window' convention

        self.program_structure()
        if self.gui_application:
            # Required Qt logic to start window
            self.app.exec_()

        sys.exit()

    def program_structure(self):
        # Get organization info so we have something to show user
        self.interface.browser.scrape_initial_org_info()
        """ 
        Main menu should show the following across interfaces:
        1. Existing VPN connections that we can connect to
        2. After list of VPN connections, have a "+ Add a connection" option
        3. Indicate which VPN connections that are currently active (if any)
        4. Route table (should change when a VPN connection is made)
        5. Latency/loss/bandwidth graph used for a connected VPN
        
        It should return the next user action
        """
        self.interface.show_main_menu()
        user_action = self.interface.get_user_action()

        if user_action == 'add vpn':
            self.interface.add_vpn()
        elif user_action == 'connect vpn':
            self.interface.connect_vpn()
            self.interface.show_result()
        elif user_action == 'troubleshoot vpn':
            self.interface.troubleshoot_vpn()
        elif user_action == 'quit':
            exit()

