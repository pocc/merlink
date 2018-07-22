#!/usr/bin/python

#  Python libraries
import sys
from PyQt5.QtWidgets import QApplication

# Local modules
from src.gui.main_window import MainWindow
from src.cli.merlink_cli import MainCli
from src.modules.data_scraper import DataScraper


class Controller:
    def __init__(self):
        super(Controller, self).__init__()

        self.browser = DataScraper()
        self.username = ''
        self.password = ''

        # If there is one argument, start GUI
        # Otherwise, start CLI
        if len(sys.argv) == 1:
            self.app = QApplication(sys.argv)
            # We want to be able to be connected with VPN with systray icon
            self.app.setQuitOnLastWindowClosed(False)
            self.interface = MainWindow()
            self.messages = self.interface.messages()
            self.app.exec_()

        else:
            self.interface = MainCli()  # After 'Main Window' convention

        self.program_structure()

        sys.exit()

    def program_structure(self):
        # vpn_username/vpn_password
        self.username, self.password = \
            self.interface.login_provider()
        self.resolve_login_attempt()
        # vpn_vars is a list of all vpn variables, including options
        vpn_vars = \
            self.interface.show_main_menu(self.username, self.password)
        # vpn_result will be 0 or the error code number
        vpn_result = \
            self.interface.attempt_vpn_connection(vpn_vars)

        self.interface.show_result(vpn_result)

    def resolve_login_attempt(self):
        self.browser.attempt_login(self.username, self.password)
        # After setup, verify whether user authenticates correctly
        result_url = self.browser.get_url()
        # URL contains /login/login if login failed
        if '/login/login' in result_url:
            self.messages.show_error_dialog(
                'ERROR: Invalid username or password.')

        # Two-Factor redirect: https://account.meraki.com/login/sms_auth?go=%2F
        elif 'sms_auth' in result_url:
            self.messages.get_tfa_dialog()
        else:
            self.messages.get_login_success()

