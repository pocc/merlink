#!/usr/bin/python

#  Python libraries
import sys
from PyQt5.QtWidgets import QApplication

# Local modules
from src.gui.main_window import MainWindow
from src.gui.login_dialog import LoginDialog
from src.gui.modal_dialogs import ModalMessages
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
        self.gui_application = (len(sys.argv) == 1)
        if self.gui_application:
            self.app = QApplication(sys.argv)
            # We want to be able to be connected with VPN with systray icon
            self.app.setQuitOnLastWindowClosed(False)
            self.interface = MainWindow()
            self.login = LoginDialog()
            self.messages = ModalMessages()

        else:
            self.interface = MainCli()  # After 'Main Window' convention

        self.messages = self.interface.messages
        self.program_structure()
        if self.gui_application:
            # Required Qt logic to start window
            self.app.exec_()

        sys.exit()

    def program_structure(self):
        login_success = False
        while not login_success:
            # Required to start login window again
            if self.gui_application:
                self.login.exec_()
            print("in login success while loop")
            self.username, self.password = self.login.get_login_info()

            # Required so that login window can be closed
            if self.gui_application:
                if self.username == '' and self.password == '':
                    sys.exit()

            print("username/password: " + self.username + self.password)
            login_success = self.check_login_attempt()

        # Get organization info so we have something to show user
        self.browser.scrape_orgs()

        # vpn_vars is a list of all vpn variables, including options
        vpn_vars = \
            self.interface.show_main_menu(self.username, self.password)
        # vpn_result will be 0 or the error code number
        vpn_result = \
            self.interface.attempt_vpn_connection(vpn_vars)

        self.interface.show_result(vpn_result)

    def check_login_attempt(self):
        self.browser.attempt_login(self.username, self.password)
        # After setup, verify whether user authenticates correctly
        result_url = self.browser.get_url()
        # URL contains /login/login if login failed
        if '/login/login' in result_url:
            self.messages.show_error_dialog(
                'ERROR: Invalid username or password.')
            self.login.password_field.setText('')
            return False

        # Two-Factor redirect: https://account.meraki.com/login/sms_auth?go=%2F
        elif 'sms_auth' in result_url:
            self.messages.get_tfa_dialog()
        else:
            return True
