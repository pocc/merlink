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
            if self.login.exec_():
                self.browser = self.login.get_browser()

        else:
            self.interface = MainCli()  # After 'Main Window' convention

        self.program_structure()
        if self.gui_application:
            # Required Qt logic to start window
            self.app.exec_()

        sys.exit()

    def program_structure(self):
        # Get organization info so we have something to show user
        self.browser.scrape_orgs()

        # vpn_vars is a list of all vpn variables, including options
        vpn_vars = \
            self.interface.show_main_menu(self.username, self.password)
        # vpn_result will be 0 or the error code number
        vpn_result = \
            self.interface.attempt_vpn_connection(vpn_vars)

        self.interface.show_result(vpn_result)