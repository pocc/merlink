#!/usr/bin/python

#  Python libraries
import sys
from PyQt5.QtWidgets import QApplication

# Local modules
from src.gui.main_window import MainWindow
from src.cli.merlink_cli import MainCli


class Controller:
    def __init__(self):
        super(Controller, self).__init__()

        # If there is one argument, start GUI
        # Otherwise, start CLI
        if len(sys.argv) == 1:
            self.app = QApplication(sys.argv)
            # We want to be able to be connected with VPN with systray icon
            self.app.setQuitOnLastWindowClosed(False)
            self.interface = MainWindow()
            self.interface.show()

            sys.exit(self.app.exec_())

        else:
            self.interface = MainCli()  # After 'Main Window' convention
            sys.exit()

    def show_login(self):
        self.interface.login_dialog()
        self.show_main_menu()

    def show_main_menu(self):
        # All organizational code should be here
        # For the time being, login to the Meraki Dashboard is required
        # for this program to funciton
        if True:
            self.attempt_vpn_connection()

    def attempt_vpn_connection():
        print("Success!")
