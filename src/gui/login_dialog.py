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
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import QPixmap

from src.modules.os_utils import pyinstaller_path
from src.modules.dashboard_browser import DataScraper
from src.gui.modal_dialogs import show_error_dialog


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

        # LOGIN WINDOW UI SETUP
        self.setModal(True)  # Make the login window prevent program usage
        self.meraki_img = QLabel('<a href=https://meraki.cisco.com/products/'
                                 'wireless#mr-new>MR advertisement</a>')
        self.meraki_img.setOpenExternalLinks(True)

        # Copying style from Dashboard Login
        # (https://account.meraki.com/login/dashboard_login)
        self.heading_style = "font-family: verdana, sans-serif; font-style: " \
                             "normal; font-size: 28px; font-weight: 300; " \
                             "color:  #606060;"
        self.label_style = "font-family: verdana, sans-serif; font-style: " \
                           "normal; font-size: 13px; color: #606060;"
        self.link_style = "font-family: verdana, sans-serif; font-style: " \
                          "normal; font-size: 13px; color: #1795E6;"

        self.heading = QLabel("Dashboard Login")
        self.heading.setStyleSheet(self.heading_style)
        self.username_lbl = QLabel("Email")
        self.username_lbl.setStyleSheet(self.label_style)
        self.password_lbl = QLabel("Password")
        self.password_lbl.setStyleSheet(self.label_style)
        self.username_field = QLineEdit(self)
        self.password_field = QLineEdit(self)
        # Set up username and password so these vars have values
        self.username = ''
        self.password = ''

        # Reset password field to '', especially if login failed
        self.password_field.setText('')

        # Masks password as a series of dots instead of characters
        self.password_field.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Log in")

        # self.login_btn.setStyleSheet(self.login_btn_style)
        self.forgot_password_lbl = \
            QLabel("<a href=\"https://account.meraki.com/login/reset_password"
                   "\" style=\"color:#1795E6;text-decoration:none\">"
                   "I forgot my password</a>")
        self.forgot_password_lbl.setStyleSheet(self.link_style)
        self.forgot_password_lbl.setOpenExternalLinks(True)
        self.create_account_lbl = \
            QLabel(" <a href=\"https://account.meraki.com/login/signup\" "
                   "style=\"color:#1795E6;text-decoration:none\">"
                   "Create an account</a>")
        self.create_account_lbl.setStyleSheet(self.link_style)
        self.create_account_lbl.setOpenExternalLinks(True)
        self.about_lbl = \
            QLabel("<a href=\"https://github.com/pocc/merlink\" style=\""
                   "color:#1795E6;text-decoration:none\">About</a>")
        self.about_lbl.setStyleSheet(self.link_style)
        self.about_lbl.setOpenExternalLinks(True)

        layout_login_options = QHBoxLayout()
        layout_login_options.addWidget(self.forgot_password_lbl)
        layout_login_options.addStretch()
        layout_login_options.addWidget(self.create_account_lbl)

        # Create a widget to contain the login layout.
        # This allows us to paint the background of the widget
        login_widget = QWidget(self)
        login_widget.setStyleSheet("background-color:white")
        # Create labels and textboxes to form a login layout
        layout_login = QVBoxLayout(login_widget)
        layout_login.addWidget(self.heading)
        layout_login.addWidget(self.username_lbl)
        layout_login.addWidget(self.username_field)
        layout_login.addWidget(self.password_lbl)
        layout_login.addWidget(self.password_field)
        layout_login.addWidget(self.login_btn)
        layout_login.addLayout(layout_login_options)
        layout_login.addStretch()
        layout_login.addWidget(self.about_lbl)

        self.meraki_img.setPixmap(
            QPixmap(pyinstaller_path('src/media/new-mr.jpg')))

        # Background for program will be #Meraki green = #78be20
        self.setStyleSheet("background-color:#eee")
        layout_main = QHBoxLayout()
        layout_main.addWidget(login_widget)
        layout_main.addWidget(self.meraki_img)
        self.setLayout(layout_main)
        self.setWindowTitle('MerLink')

        # Required to have this class variables as it is not possible to
        # return/pass values to/from triggered functions (self.tfa_verify)
        self.tfa_success = False
        self.get_twofactor_code = QLineEdit()
        self.twofactor_dialog = QDialog()

        # INIT THIS OBJECT
        self.show_login()

    def show_login(self):
        """Shows the login window and records if the login button is pressed.

        If the login button is pressed, check whether the credentials are
        valid by sending them to the virtual browser.
        """

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

