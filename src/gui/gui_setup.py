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

"""Main window UI creates much of the GUI application."""
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QDialog
from PyQt5.Qt import QPixmap

from src.modules.os_utils import pyinstaller_path


class GuiSetup:
    """Takes a Qt windor or dialog object and then decorates it like a cake.

    This file exists to take much of the UI content of the MainWindow and
    LoginDialog classes so that the Qt elements in this project are more
    properly segmented off. This is in lieu of having created the UI files in
    Qt Designer, converted them to pyuic, and then never touched the UI
    files again (not a route I chose to go).

    Attributes:
        app (Qt Objct): The window/dialog object that this class decorates.
    """
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self, app):
        self.app = app
        
    def login_dialog_setup(self):
        """LOGIN WINDOW UI SETUP"""
        self.app.setModal(True)  # Make the login window prevent program usage
        self.app.meraki_img = QLabel('<a href=https://meraki.cisco.com/products'
                                     '/wireless#mr-new>MR advertisement</a>')
        self.app.meraki_img.setOpenExternalLinks(True)

        # Copying style from Dashboard Login
        # (https://account.meraki.com/login/dashboard_login)
        self.app.heading_style = \
            "font-family: verdana, sans-serif; font-style: normal; font-size:" \
            " 28px; font-weight: 300; color:  #606060;"
        self.app.label_style = "font-family: verdana, sans-serif; font-style:" \
                               " normal; font-size: 13px; color: #606060;"
        self.app.link_style = "font-family: verdana, sans-serif; font-style:" \
                              " normal; font-size: 13px; color: #1795E6;"
        self.app.heading = QLabel("Dashboard Login")
        self.app.heading.setStyleSheet(self.app.heading_style)
        self.app.username_lbl = QLabel("Email")
        self.app.username_lbl.setStyleSheet(self.app.label_style)
        self.app.password_lbl = QLabel("Password")
        self.app.password_lbl.setStyleSheet(self.app.label_style)
        self.app.username_field = QLineEdit(self.app)
        self.app.password_field = QLineEdit(self.app)
        # Set up username and password so these vars have values
        self.app.username = ''
        self.app.password = ''

        # Reset password field to '', especially if login failed
        self.app.password_field.setText('')

        # Masks password as a series of dots instead of characters
        self.app.password_field.setEchoMode(QLineEdit.Password)
        self.app.login_btn = QPushButton("Log in")

        # self.app.login_btn.setStyleSheet(self.app.login_btn_style)
        self.app.forgot_password_lbl = \
            QLabel("<a href=\"https://account.meraki.com/login/reset_password"
                   "\" style=\"color:#1795E6;text-decoration:none\">"
                   "I forgot my password</a>")
        self.app.forgot_password_lbl.setStyleSheet(self.app.link_style)
        self.app.forgot_password_lbl.setOpenExternalLinks(True)
        self.app.create_account_lbl = \
            QLabel(" <a href=\"https://account.meraki.com/login/signup\" "
                   "style=\"color:#1795E6;text-decoration:none\">"
                   "Create an account</a>")
        self.app.create_account_lbl.setStyleSheet(self.app.link_style)
        self.app.create_account_lbl.setOpenExternalLinks(True)
        self.app.about_lbl = \
            QLabel("<a href=\"https://github.com/pocc/merlink\" style=\""
                   "color:#1795E6;text-decoration:none\">About</a>")
        self.app.about_lbl.setStyleSheet(self.app.link_style)
        self.app.about_lbl.setOpenExternalLinks(True)

        layout_login_options = QHBoxLayout()
        layout_login_options.addWidget(self.app.forgot_password_lbl)
        layout_login_options.addStretch()
        layout_login_options.addWidget(self.app.create_account_lbl)

        # Create a widget to contain the login layout.
        # This allows us to paint the background of the widget
        login_widget = QWidget(self.app)
        login_widget.setStyleSheet("background-color:white")
        # Create labels and textboxes to form a login layout
        layout_login = QVBoxLayout(login_widget)
        layout_login.addWidget(self.app.heading)
        layout_login.addWidget(self.app.username_lbl)
        layout_login.addWidget(self.app.username_field)
        layout_login.addWidget(self.app.password_lbl)
        layout_login.addWidget(self.app.password_field)
        layout_login.addWidget(self.app.login_btn)
        layout_login.addLayout(layout_login_options)
        layout_login.addStretch()
        layout_login.addWidget(self.app.about_lbl)

        self.app.meraki_img.setPixmap(
            QPixmap(pyinstaller_path('src/media/new-mr.jpg')))

        # Background for program will be #Meraki green = #78be20
        self.app.setStyleSheet("background-color:#eee")
        layout_main = QHBoxLayout()
        layout_main.addWidget(login_widget)
        layout_main.addWidget(self.app.meraki_img)
        self.app.setLayout(layout_main)
        self.app.setWindowTitle('MerLink')

        # Required to have this class variables as it is not possible to
        # return/pass values to/from triggered functions (self.app.tfa_verify)
        self.app.tfa_success = False
        self.app.get_twofactor_code = QLineEdit()
        self.app.twofactor_dialog = QDialog()

    def main_window_setup(self):
        """Set up the Main Window's Qt elements"""
        # QMainWindow requires that a central app be set
        self.app.cw = QWidget(self.app)
        self.app.setCentralWidget(self.app.cw)
        # CURRENT minimum width of Main Window
        # SUBJECT TO CHANGE as features are added
        # self.cw.setMinimumWidth(400)

        self.app.setWindowTitle('Merlink - VPN Client for Meraki firewalls')
        
        # Create a horizontal line above the status bar to highlight it        
        self.app.hline = QFrame()
        self.app.hline.setFrameShape(QFrame.HLine)
        self.app.hline.setFrameShadow(QFrame.Sunken)
        
        self.app.status = QStatusBar()
        self.app.status.showMessage("Status: Select organization")
        self.app.status.setStyleSheet("Background: white")

        # Set initial vars for username/password fields for dasboard/guest user
        self.app.radio_username_label = QLabel("Email")
        self.app.radio_username_label.setStyleSheet("color: #606060")  # Gray
        self.app.radio_username_textfield = QLineEdit()
        self.app.radio_password_label = QLabel("Password")
        self.app.radio_password_label.setStyleSheet("color: #606060")  # Gray
        self.app.radio_password_textfield = QLineEdit()
        self.app.radio_password_textfield.setEchoMode(QLineEdit.Password)
        
        # Title is an NSIS uninstall reference (see Modern.nsh)
        self.app.org_dropdown = QComboBox()
        self.app.org_dropdown.addItem('-- Select an Organization --')
        self.app.network_dropdown = QComboBox()
        self.app.network_dropdown.setEnabled(False)
        
        self.app.user_auth_section = QVBoxLayout()
        self.app.radio_user_layout = QHBoxLayout()
        self.app.user_auth_section.addLayout(self.app.radio_user_layout)
        self.app.radio_dashboard_admin_user = QRadioButton("Dashboard Admin")
        # Default is to have dashboard user
        self.app.radio_dashboard_admin_user.setChecked(True)
        self.app.radio_guest_user = QRadioButton("Guest User")
        self.app.radio_user_layout.addWidget(
            self.app.radio_dashboard_admin_user)
        self.app.radio_user_layout.addWidget(self.app.radio_guest_user)
        self.app.radio_dashboard_admin_user.toggled.connect(
            self.set_dashboard_user_layout)
        self.app.radio_guest_user.toggled.connect(self.set_guest_user_layout)

        self.app.user_auth_section.addWidget(self.app.radio_username_label)
        self.app.user_auth_section.addWidget(self.app.radio_username_textfield)
        self.app.user_auth_section.addWidget(self.app.radio_password_label)
        self.app.user_auth_section.addWidget(self.app.radio_password_textfield)
        
        # Ask the user for int/str values if they want to enter them
        self.app.idle_disconnect_layout = QHBoxLayout()
        self.app.idle_disconnect_chkbox = QCheckBox("Idle disconnect seconds?")
        self.app.idle_disconnect_spinbox = QSpinBox()
        self.app.idle_disconnect_spinbox.setValue(0)
        # Negative seconds aren't useful here
        self.app.idle_disconnect_spinbox.setMinimum(0)
        self.app.idle_disconnect_layout.addWidget(
            self.app.idle_disconnect_chkbox)
        self.app.idle_disconnect_layout.addWidget(
            self.app.idle_disconnect_spinbox)
        
        self.app.dns_suffix_layout = QHBoxLayout()
        self.app.dns_suffix_chkbox = QCheckBox("DNS Suffix?") 
        self.app.dns_suffix_txtbox = QLineEdit('-')
        self.app.dns_suffix_layout.addWidget(
            self.app.dns_suffix_chkbox)
        self.app.dns_suffix_layout.addWidget(
            self.app.dns_suffix_txtbox)
        
        # Boolean asks of the user
        self.app.split_tunneled_chkbox = QCheckBox("Split-Tunnel?")
        self.app.remember_credential_chkbox = QCheckBox("Remember Credentials?")
        self.app.use_winlogon_chkbox = QCheckBox(
            "Use Windows Logon Credentials?")
        
        self.app.connect_btn = QPushButton("Connect")
        vert_layout = QVBoxLayout()

        # Add Dashboard Entry-only dropdowns
        vert_layout.addWidget(self.app.org_dropdown)
        vert_layout.addWidget(self.app.network_dropdown)
        vert_layout.addLayout(self.app.user_auth_section)

        # Add layouts for specialized params
        vert_layout.addLayout(self.app.idle_disconnect_layout)
        vert_layout.addLayout(self.app.dns_suffix_layout)

        # Add checkboxes
        vert_layout.addWidget(self.app.split_tunneled_chkbox)
        vert_layout.addWidget(self.app.remember_credential_chkbox)
        vert_layout.addWidget(self.app.use_winlogon_chkbox)

        # Add stuff at bottom
        vert_layout.addWidget(self.app.connect_btn)
        vert_layout.addWidget(self.app.hline)
        vert_layout.addWidget(self.app.status)

        self.app.cw.setLayout(vert_layout)

    def set_dashboard_user_layout(self):
        """Set the dashboard user layout

        Hides guest user layout as we will only be connecting with one user.
        The user will see the username/obfuscated password they entered."""

        self.app.radio_username_textfield.setText(self.app.browser.username)
        self.app.radio_username_textfield.setReadOnly(True)
        self.app.radio_password_textfield.setText(self.app.browser.password)
        self.app.radio_password_textfield.setReadOnly(True)

    def set_guest_user_layout(self):
        """Set the guest user layout

        Hides dashboard user layout as we will only be connecting with one user.
        The user will see blank user/pass text fields where they can enter
        information for a guest user."""

        self.app.radio_username_textfield.clear()
        self.app.radio_username_textfield.setReadOnly(False)
        self.app.radio_password_textfield.clear()
        self.app.radio_password_textfield.setReadOnly(False)
