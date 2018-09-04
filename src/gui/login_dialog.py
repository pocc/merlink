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
from src.gui.gui_setup import GuiSetup


class LoginDialog(QDialog):
    """This class provides dialog GUI elements.

    Attributes:
        browser (MechanicalSoup): A browser in which to store user credentials.

        ----

        Please consider moving the brunt of the __init__ UI content to its
        own file.

    TODO: Convert the other attributes to a dict
    """
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self):
        """Create UI vars necessary for login window to be shown."""
        super(LoginDialog, self).__init__()
        self.browser = DataScraper()
        self.login_window_qt = GuiSetup(self)
        self.show_login()

    def show_login(self):
        """Shows the login window and records if the login button is pressed.

        If the login button is pressed, check whether the credentials are
        valid by sending them to the virtual browser.
        """
        self.login_window_qt.login_dialog_setup()
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
        # TWOFACTOR_DIALOG UI SETUP #
        self.get_twofactor_code.clear()  # Clear if exists
        # QDialog that gets 6 digit two-factor code
        self.twofactor_dialog.setWindowTitle("Two-Factor Authentication")
        dialog_layout = QVBoxLayout()
        twofactor_code_layout = QHBoxLayout()

        twofactor_code_label = QLabel("Enter verification code")
        twofactor_dialog_yesno = QHBoxLayout()
        yesbutton = QPushButton("Verify")
        yesbutton.setToolTip("Attempt connection with this tfa code")
        nobutton = QPushButton("Cancel")
        yesbutton.setToolTip("Quit")
        twofactor_dialog_yesno.addWidget(yesbutton)
        twofactor_dialog_yesno.addWidget(nobutton)

        # Layout code
        twofactor_code_layout.addWidget(twofactor_code_label)
        twofactor_code_layout.addWidget(self.get_twofactor_code)
        dialog_layout.addLayout(twofactor_code_layout)
        # dialog_layout.addWidget(self.get_remember_choice)
        dialog_layout.addLayout(twofactor_dialog_yesno)
        self.twofactor_dialog.setLayout(dialog_layout)

        yesbutton.clicked.connect(self.tfa_verify)
        nobutton.clicked.connect(self.twofactor_dialog.close)
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

