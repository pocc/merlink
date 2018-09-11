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
import sys

from PyQt5.QtWidgets import QDialog

from src.dashboard_browser.dashboard_browser import DashboardBrowser
from src.gui.modal_dialogs import show_error_dialog
import src.gui.gui_setup as guify


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
        self.browser = DashboardBrowser()
        self.tfa_success = False
        self.login_dict = {'username': '', 'password': ''}
        self.show_login()

    def show_login(self):
        """Show the login window and records if the login button is pressed.

        Uses methods stored in gui_setup to decorate the dialog object.
        If the login button is pressed, check whether the credentials are
        valid by sending them to the virtual browser.
        """
        # Decorate login window with gui functions
        guify.login_widget_setup(self)
        guify.login_window_setup(self)
        guify.login_set_layout(self)
        guify.login_tfa_set_layout(self)

        self.show()
        self.login_btn.clicked.connect(self.check_login_attempt)

    def get_login_info(self):
        """Return the values currently in the user/pass text fields."""
        return self.username_field.text(), self.password_field.text()

    def check_login_attempt(self):
        """Verify whether entered username/password combination is correct.

        NOTE: Keeping this code in here even though it's interface-independent.
        If we don't keep this here, then the login button will need to connect
        to self.close. It may look weird if the login window closes due to
        the user incorrectly entering user/pass and then reopens
        """
        username = self.username_field.text()
        password = self.password_field.text()
        result = self.browser.attempt_login(username, password)

        if result == 'auth_error':
            show_error_dialog('ERROR: Invalid username or password.')
            self.password_field.setText('')
        elif result == 'sms_auth':
            self.tfa_dialog_setup()
            self.close()
        elif result == 'auth_success':
            self.login_dict['username'] = username
            self.login_dict['password'] = password
            self.close()
        elif result == 'ConnectionError':
            show_error_dialog("""ERROR: No internet connection!\n\nAccess to
                the internet is required for MerLink to work. Please check
                your network settings and try again. Now exiting...""")
            sys.exit()
        else:
            show_error_dialog("ERROR: Invalid authentication type!")

    def tfa_dialog_setup(self):
        """Create and execute the UI for the TFA dialog."""
        # Create dialog window with login window object
        guify.tfa_widget_setup(self)
        guify.tfa_set_layout(self)

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
