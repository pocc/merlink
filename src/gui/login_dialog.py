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

"""Login dialog GUI elements."""
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout

from src.modules.dashboard_browser import DataScraper
from src.gui.modal_dialogs import show_error_dialog
import src.gui.gui_setup as gui_setup


class LoginDialog(QDialog):
    """This class provides dialog GUI elements.

    Attributes:
        browser (MechanicalSoup): A browser in which to store user credentials.
    """
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self):
        """Create UI vars necessary for login window to be shown."""
        super(LoginDialog, self).__init__()
        self.browser = DataScraper()
        self.tfa_success = False
        self.show_login()

    def show_login(self):
        """Shows the login window and records if the login button is pressed.

        Uses methods stored in gui_setup to decorate the dialog object.
        If the login button is pressed, check whether the credentials are
        valid by sending them to the virtual browser.
        """
        # Decorate login window with gui functions
        gui_setup.login_widget_setup(self)
        gui_setup.login_window_setup(self)
        gui_setup.login_set_layout(self)
        gui_setup.login_tfa_set_layout(self)

        self.show()
        self.login_btn.clicked.connect(self.check_login_attempt)

    def get_login_info(self):
        """Returns the values currently in the user/pass text fields"""
        return self.username_field.text(), self.password_field.text()

    def get_browser(self):
        """Returns the browser object that has the credentials cookie."""
        return self.browser

    def check_login_attempt(self):
        """Verifies whether entered username/password combination is correct

        NOTE: Keeping this code in here even though it is interface-independent.
        If we don't keep this here, then the login button will need to connect
        to self.close. It may look weird if the login window closes due to
        the user incorrectly entering user/pass and then reopens
        """

        result = self.browser.attempt_login(
            self.username_field.text(),
            self.password_field.text()
        )

        if result == 'auth_error':
            show_error_dialog('ERROR: Invalid username or password.')
            self.password_field.setText('')
        elif result == 'sms_auth':
            self.tfa_dialog_setup()
            self.close()
        elif result == 'auth_success':
            self.close()
        else:
            show_error_dialog("ERROR: Invalid authentication type!")

    def tfa_dialog_setup(self):
        """Create and execute the UI for the TFA dialog"""
        # Create dialog window with login window object
        gui_setup.tfa_widget_setup(self)
        gui_setup.tfa_set_layout(self)

        self.yesbutton.clicked.connect(self.tfa_verify)
        self.nobutton.clicked.connect(self.twofactor_dialog.close)
        while not self.tfa_success:
            self.twofactor_dialog.exec_()

    def tfa_verify(self):
        """Submit the tfa code and communicate success/failure to user.

        This fn is partially required because we need a function to connect
        to the button click signal.
        """
        self.tfa_success = self.browser.tfa_submit_info(
            self.get_twofactor_code.text())
        if self.tfa_success:
            self.twofactor_dialog.accept()
        else:
            show_error_dialog('ERROR: Invalid verification code!')

