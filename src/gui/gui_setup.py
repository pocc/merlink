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
"""Functions that take a Qt object and decorate it like a cake.

This file exists to take much of the UI content of the MainWindow and
LoginDialog classes so that the Qt elements in this project are more
properly segmented off. This is in lieu of having created the UI files in
Qt Designer, converted them to pyuic, and then never touched the UI
files again (not a route I chose to go).

Args (for any function):
    app (Qt Object): The window/dialog object that this function decorates.
"""
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


def login_widget_setup(app):
    """Take login app and add widgets to it."""
    # Copying style from Dashboard Login
    # (https://account.meraki.com/login/dashboard_login)
    app.heading_style = \
        "font-family: verdana, sans-serif; font-style: normal; font-size:" \
        " 28px; font-weight: 300; color:  #606060;"
    app.label_style = "font-family: verdana, sans-serif; font-style:" \
                      " normal; font-size: 13px; color: #606060;"
    app.link_style = "font-family: verdana, sans-serif; font-style:" \
                     " normal; font-size: 13px; color: #1795E6;"
    app.heading = QLabel("Dashboard Login")
    app.heading.setStyleSheet(app.heading_style)
    app.username_lbl = QLabel("Email")
    app.username_lbl.setStyleSheet(app.label_style)
    app.password_lbl = QLabel("Password")
    app.password_lbl.setStyleSheet(app.label_style)
    app.username_field = QLineEdit(app)
    app.password_field = QLineEdit(app)
    # Reset password field to '', especially if login failed
    app.password_field.setText('')
    # Masks password as a series of dots instead of characters
    app.password_field.setEchoMode(QLineEdit.Password)
    app.login_btn = QPushButton("Log in")

    # app.login_btn.setStyleSheet(app.login_btn_style)
    app.forgot_password_lbl = \
        QLabel("<a href=\"https://account.meraki.com/login/reset_password"
               "\" style=\"color:#1795E6;text-decoration:none\">"
               "I forgot my password</a>")
    app.forgot_password_lbl.setStyleSheet(app.link_style)
    app.forgot_password_lbl.setOpenExternalLinks(True)
    app.create_account_lbl = \
        QLabel(" <a href=\"https://account.meraki.com/login/signup\" "
               "style=\"color:#1795E6;text-decoration:none\">"
               "Create an account</a>")
    app.create_account_lbl.setStyleSheet(app.link_style)
    app.create_account_lbl.setOpenExternalLinks(True)
    app.about_lbl = \
        QLabel("<a href=\"https://github.com/pocc/merlink\" style=\""
               "color:#1795E6;text-decoration:none\">About</a>")
    app.about_lbl.setStyleSheet(app.link_style)
    app.about_lbl.setOpenExternalLinks(True)

    # Set up username and password so these vars have values
    app.username = ''
    app.password = ''


def login_window_setup(app):
    """Set options for the login widnow itapp."""
    app.setModal(True)  # Make the login window prevent program usage
    app.meraki_img = QLabel('<a href=https://meraki.cisco.com/products'
                            '/wireless#mr-new>MR advertisement</a>')
    app.meraki_img.setOpenExternalLinks(True)
    app.meraki_img.setPixmap(QPixmap(pyinstaller_path('src/media/new-mr.jpg')))
    # Background for program will be #Meraki green = #78be20
    app.setStyleSheet("background-color:#eee")
    app.setWindowTitle('MerLink - Login Window')


def login_set_layout(app):
    """Tie login layout to QDialog object."""
    layout_login_options = QHBoxLayout()
    layout_login_options.addWidget(app.forgot_password_lbl)
    layout_login_options.addStretch()
    layout_login_options.addWidget(app.create_account_lbl)

    # Create a widget to contain the login layout.
    # This allows us to paint the background of the widget
    login_widget = QWidget(app)
    login_widget.setStyleSheet("background-color:white")
    # Create labels and textboxes to form a login layout
    layout_login = QVBoxLayout(login_widget)
    layout_login.addWidget(app.heading)
    layout_login.addWidget(app.username_lbl)
    layout_login.addWidget(app.username_field)
    layout_login.addWidget(app.password_lbl)
    layout_login.addWidget(app.password_field)
    layout_login.addWidget(app.login_btn)
    layout_login.addLayout(layout_login_options)
    layout_login.addStretch()
    layout_login.addWidget(app.about_lbl)

    layout_main = QHBoxLayout()
    layout_main.addWidget(login_widget)
    layout_main.addWidget(app.meraki_img)
    app.setLayout(layout_main)


def login_tfa_set_layout(app):
    """Set the layout for the tfa dialog."""
    # Required to have this class variables as it is not possible to
    # return/pass values to/from triggered functions (app.tfa_verify)
    app.get_twofactor_code = QLineEdit()
    app.twofactor_dialog = QDialog()


def tfa_widget_setup(app):
    """TWOFACTOR_DIALOG UI SETUP"""
    app.get_twofactor_code.clear()  # Clear if exists
    # QDialog that gets 6 digit two-factor code
    app.twofactor_dialog.setWindowTitle("Two-Factor Authentication")

    app.twofactor_code_label = QLabel("Enter verification code")
    app.twofactor_dialog_yesno = QHBoxLayout()
    app.yesbutton = QPushButton("Verify")
    app.yesbutton.setToolTip("Attempt connection with this tfa code")
    app.nobutton = QPushButton("Cancel")
    app.yesbutton.setToolTip("Quit")
    app.twofactor_dialog_yesno.addWidget(app.yesbutton)
    app.twofactor_dialog_yesno.addWidget(app.nobutton)


def tfa_set_layout(app):
    """Set up TFA layout."""
    # Layout code
    dialog_layout = QVBoxLayout()
    twofactor_code_layout = QHBoxLayout()
    twofactor_code_layout.addWidget(app.twofactor_code_label)
    twofactor_code_layout.addWidget(app.get_twofactor_code)
    dialog_layout.addLayout(twofactor_code_layout)
    # dialog_layout.addWidget(app.get_remember_choice)
    dialog_layout.addLayout(app.twofactor_dialog_yesno)
    app.twofactor_dialog.setLayout(dialog_layout)


def main_window_widget_setup(app):
    """Sets up the main window object and org/net dropdowns."""
    # QMainWindow requires that a central app be set
    app.cw = QWidget(app)
    app.setCentralWidget(app.cw)
    # Set minimum width of Main Window to 500 pixels
    app.cw.setMinimumWidth(500)
    app.setWindowTitle('MerLink - VPN Client for Meraki firewalls')

    # Create org and network dropdowns so the user can select the firewall
    # they would like to connect to.
    app.org_dropdown = QComboBox()
    app.org_dropdown.addItem('-- Select an Organization --')
    app.network_dropdown = QComboBox()
    app.network_dropdown.setEnabled(False)


def main_window_user_auth_setup(app):
    """Set initial vars for username/password fields for dasboard/guest user"""
    app.radio_username_label = QLabel("Email")
    app.radio_username_label.setStyleSheet("color: #606060")  # Gray
    app.radio_username_textfield = QLineEdit()
    app.radio_password_label = QLabel("Password")
    app.radio_password_label.setStyleSheet("color: #606060")  # Gray
    app.radio_password_textfield = QLineEdit()
    app.radio_password_textfield.setEchoMode(QLineEdit.Password)

    app.user_auth_section = QVBoxLayout()
    app.radio_user_layout = QHBoxLayout()
    app.user_auth_section.addLayout(app.radio_user_layout)
    app.radio_admin_user = QRadioButton("Dashboard Admin")
    # Default is to have dashboard user
    app.radio_admin_user.setChecked(True)
    app.radio_guest_user = QRadioButton("Guest User")
    app.radio_user_layout.addWidget(app.radio_admin_user)
    app.radio_user_layout.addWidget(app.radio_guest_user)
    app.user_auth_section.addWidget(app.radio_username_label)
    app.user_auth_section.addWidget(app.radio_username_textfield)
    app.user_auth_section.addWidget(app.radio_password_label)
    app.user_auth_section.addWidget(app.radio_password_textfield)


def main_window_vpn_vars_setup(app):
    """Setup the vpn vars region."""
    # Allow the user to change the VPN name
    app.vpn_name_layout = QHBoxLayout()
    app.vpn_name_label = QLabel("VPN Name:")
    app.vpn_name_textfield = QLineEdit()
    app.vpn_name_layout.addWidget(app.vpn_name_label)
    app.vpn_name_layout.addWidget(app.vpn_name_textfield)

    # Ask the user for int/str values if they want to enter them
    app.idle_disconnect_layout = QHBoxLayout()
    app.idle_disconnect_chkbox = QCheckBox("Idle disconnect seconds?")
    app.idle_disconnect_spinbox = QSpinBox()
    app.idle_disconnect_spinbox.setValue(0)
    # Negative seconds aren't useful here
    app.idle_disconnect_spinbox.setMinimum(0)
    app.idle_disconnect_layout.addWidget(app.idle_disconnect_chkbox)
    app.idle_disconnect_layout.addWidget(app.idle_disconnect_spinbox)

    app.dns_suffix_layout = QHBoxLayout()
    app.dns_suffix_chkbox = QCheckBox("DNS Suffix?")
    app.dns_suffix_txtbox = QLineEdit('-')
    app.dns_suffix_layout.addWidget(app.dns_suffix_chkbox)
    app.dns_suffix_layout.addWidget(app.dns_suffix_txtbox)

    # Boolean asks of the user
    app.split_tunneled_chkbox = QCheckBox("Split-Tunnel?")
    app.remember_credential_chkbox = QCheckBox("Remember Credentials?")
    app.use_winlogon_chkbox = QCheckBox("Use Windows Logon Credentials?")

    app.connect_btn = QPushButton("Connect")

    # Status bar setup
    # Create a horizontal line above the status bar to highlight it
    app.hline = QFrame()
    app.hline.setFrameShape(QFrame.HLine)
    app.hline.setFrameShadow(QFrame.Sunken)
    # Status bar be at bottom and inform user of what the program is doing.
    app.status = QStatusBar()
    app.status.showMessage("Status: Select organization")
    app.status.setStyleSheet("Background: white")


def main_window_set_layout(app):
    """Create a main vertical layout that may contain other layouts."""
    vert_layout = QVBoxLayout()
    vert_layout.addWidget(app.org_dropdown)
    vert_layout.addWidget(app.network_dropdown)
    vert_layout.addLayout(app.user_auth_section)
    vert_layout.addLayout(app.vpn_name_layout)

    # Add layouts for specialized params
    vert_layout.addLayout(app.idle_disconnect_layout)
    vert_layout.addLayout(app.dns_suffix_layout)

    # Add checkboxes
    vert_layout.addWidget(app.split_tunneled_chkbox)
    vert_layout.addWidget(app.remember_credential_chkbox)
    vert_layout.addWidget(app.use_winlogon_chkbox)

    # Add stuff at bottom
    vert_layout.addWidget(app.connect_btn)
    vert_layout.addWidget(app.hline)
    vert_layout.addWidget(app.status)

    # Tie main layout to central window object (REQUIRED)
    app.cw.setLayout(vert_layout)


def main_window_set_admin_layout(app):
    """Set the dashboard user layout

    Hides guest user layout as we will only be connecting with one user.
    The user will see the username/obfuscated password they entered."""

    app.radio_username_textfield.setText(app.browser.username)
    app.radio_username_textfield.setReadOnly(True)
    app.radio_password_textfield.setText(app.browser.password)
    app.radio_password_textfield.setReadOnly(True)


def main_window_set_guest_layout(app):
    """Set the guest user layout

    Hides dashboard user layout as we will only be connecting with one user.
    The user will see blank user/pass text fields where they can enter
    information for a guest user."""

    app.radio_username_textfield.clear()
    app.radio_username_textfield.setReadOnly(False)
    app.radio_password_textfield.clear()
    app.radio_password_textfield.setReadOnly(False)
