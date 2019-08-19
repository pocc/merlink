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

All classes that are Ui related should end with 'Ui'.

Args (for any function):
    app (Qt Object): The window/dialog object that this function decorates.
"""
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.Qt import QSizePolicy

from merlink.qt.gui_utils import disable_lineedit


def is_layout(obj):
    """Check whether the object is a layout of one type."""
    return isinstance(obj, QHBoxLayout) or isinstance(obj, QVBoxLayout)


class MainWindowUi(QMainWindow):
    """This class manages the system tray icon of the main program, post-login.
    """

    vpn_connect_section = QVBoxLayout()

    def __init__(self):
        super(QMainWindow, self).__init__()
        # Using a StackedWidget to be able to replace login window
        # https://stackoverflow.com/questions/13550076
        self.cw = QWidget()
        self.setCentralWidget(self.cw)
        # Set minimum width of Main Window to 500 pixels
        self.cw.setMinimumWidth(500)
        self.setWindowTitle('MerLink - VPN Client for Meraki firewalls')
        self.link_style = "font-family: verdana, sans-serif; font-style:" \
                          " normal; font-size: 13px; color: #1795E6;"

        # Required for Login. Elements should be object variables if they
        # Could be called by other modules
        self.username_textfield = QLineEdit()
        self.password_textfield = QLineEdit()
        self.guest_user_chkbox = QCheckBox("Use guest account instead")
        self.password_textfield.setEchoMode(QLineEdit.Password)
        self.org_dropdown = QComboBox()
        self.create_vpn_btn = QPushButton("Create VPN Interface")
        self.org_dropdown = QComboBox()
        self.network_dropdown = QComboBox()
        self.idle_disconnect_chkbox = QCheckBox("Idle disconnect seconds?")
        self.idle_disconnect_spinbox = QSpinBox()
        self.connect_vpn_btn = QPushButton("Connect")

        self.hline = QFrame()
        self.vline = QFrame()
        self.status = QStatusBar()
        self.vpn_name_textfield = QLineEdit()

        self.create_vpn_tabs = QTabWidget()
        self.tab_dashboard = QWidget()
        self.tab_manual = QWidget()
        self.vpn_opts_layout = QVBoxLayout()

    def setup_main_window(self):
        """Setup various sections that will be combined."""
        self.create_vpn_tabs.addTab(self.tab_dashboard, "Dashboard Setup")
        self.create_vpn_tabs.addTab(self.tab_manual, "Manual Setup")

        self.vpn_opts_setup()
        self.setup_manual_tab()
        self.setup_dashboard_tab()
        self.vpn_connect_setup()

        self.decorate_sections()
        self.combine_sections_dashboard()

        # Set the layout once we are done adding elements
        self.main_window_set_admin_layout()
        self.show()

    def setup_dashboard_tab(self):
        """Provide input fields for dashboard-gathered data."""
        self.tab_dashboard.layout = QVBoxLayout()

        # Guest users should manually enter their information
        # Only difference between Guest and Dashboard for UI should be that
        # Email/pass is prepopulated for dashboard admins (inactivated)
        email_pass_layout = QVBoxLayout()
        username_label = QLabel("Email")
        password_label = QLabel("Password")
        self.disable_email_pass(True)
        self.add_all_to_layout(
            email_pass_layout,
            [
                username_label,
                self.username_textfield,
                password_label,
                self.password_textfield
            ]
        )
        self.tab_dashboard.layout.addWidget(self.guest_user_chkbox)
        self.tab_dashboard.layout.addLayout(email_pass_layout)
        self.tab_dashboard.layout.addLayout(self.vpn_opts_layout)
        self.tab_dashboard.setLayout(self.tab_dashboard.layout)

    def disable_email_pass(self, change_to_disabled):
        """Disable username/password if user should not edit them."""
        disable_lineedit(self.username_textfield, change_to_disabled)
        disable_lineedit(self.password_textfield, change_to_disabled)

    def vpn_opts_setup(self):
        """Set up the vpn vars UI region."""
        # Create org and network dropdowns so the user can select the firewall
        # they would like to connect to.
        self.org_dropdown.addItem('-- Select an Organization --')
        self.network_dropdown.setEnabled(False)

        # Allow the user to change the VPN name
        vpn_name_layout = QHBoxLayout()
        vpn_name_label = QLabel("VPN Name:")
        vpn_name_layout.addWidget(vpn_name_label)
        vpn_name_layout.addWidget(self.vpn_name_textfield)

        # Ask the user for int/str values if they want to enter them
        idle_disconnect_layout = QHBoxLayout()
        self.idle_disconnect_spinbox.setValue(0)
        # Negative seconds aren't useful here
        self.idle_disconnect_spinbox.setMinimum(0)
        idle_disconnect_layout.addWidget(
            self.idle_disconnect_chkbox)
        idle_disconnect_layout.addWidget(
            self.idle_disconnect_spinbox)

        dns_suffix_layout = QHBoxLayout()
        dns_suffix_chkbox = QCheckBox("DNS Suffix?")
        dns_suffix_txtbox = QLineEdit('-')
        dns_suffix_layout.addWidget(dns_suffix_chkbox)
        dns_suffix_layout.addWidget(dns_suffix_txtbox)

        # Boolean asks of the user
        split_tunneled_chkbox = QCheckBox("Split-Tunnel?")
        remember_credential_chkbox = QCheckBox("Remember Credentials?")
        use_winlogon_chkbox = QCheckBox("Use Windows Logon Credentials?")

        self.add_all_to_layout(
            self.vpn_opts_layout,
            [
                self.org_dropdown,
                self.network_dropdown,
                vpn_name_layout,
                # Add layouts for specialized params
                idle_disconnect_layout,
                dns_suffix_layout,
                # Add checkboxes
                split_tunneled_chkbox,
                remember_credential_chkbox,
                use_winlogon_chkbox,
                # Ensure that button is at bottom of pane by adding space
                QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
            ]
        )

    def setup_manual_tab(self):
        """Gray out options and provide input fields to manually enter data."""
        self.tab_manual.layout = QVBoxLayout()
        # User should be able to change email/pass as it's required
        self.disable_email_pass(False)
        username_textfield = QLineEdit()
        password_textfield = QLineEdit()
        password_textfield.setEchoMode(QLineEdit.Password)
        username_label = QLabel("Email")
        password_label = QLabel("Password")
        vpn_name_label = QLabel("VPN Name")
        server_name_label = QLabel("Server name/IP")
        server_name_textfield = QLineEdit()
        shared_secret_label = QLabel("Shared Secret")
        shared_secret_textfield = QLineEdit()
        shared_secret_textfield.setEchoMode(QLineEdit.Password)
        self.add_all_to_layout(
            self.tab_manual.layout,
            [
                username_label,
                username_textfield,
                password_label,
                password_textfield,
                vpn_name_label,
                self.vpn_name_textfield,
                server_name_label,
                server_name_textfield,
                shared_secret_label,
                shared_secret_textfield,
                QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
            ]
        )
        self.tab_manual.setLayout(self.tab_manual.layout)

    def vpn_connect_setup(self):
        """Setup the GUI componentst of the right pane."""
        vpn_list = QListWidget()
        ipsum_vpn_interfaces = ['eth', 'wifi']
        vpn_list.addItems(ipsum_vpn_interfaces)

        check_for_probs_cb = QCheckBox(
            "Check for issues before connecting (recommended)")
        check_for_probs_cb.setChecked(True)
        probs_list = QListWidget()
        problems = ["Forget the milk", "My hovercraft is full of eels"]
        probs_list.addItems(problems)

        self.add_all_to_layout(
            self.vpn_connect_section,
            [
                vpn_list,
                check_for_probs_cb,
                probs_list,
                self.connect_vpn_btn
            ]
        )

    def decorate_sections(self):
        """Add a box around each section for readability."""
        # Set GroupBox CSS manually because otherwise margins are huge
        self.setStyleSheet(".QGroupBox {  border: 1px solid #ccc;}")

    def combine_sections_dashboard(self):
        """Combine left and right panes into a final layout."""
         # Create a horizontal line above the status bar to highlight it
        self.hline.setFrameShape(QFrame.HLine)
        self.hline.setFrameShadow(QFrame.Sunken)
        self.vline.setFrameShape(QFrame.VLine)
        self.vline.setFrameShadow(QFrame.Sunken)
        # Status bar be at bottom and inform user of what the program is doing.
        self.status.showMessage("Status: -")
        self.status.setStyleSheet("Background:#fff")

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        left_pane = QVBoxLayout()
        left_pane.addWidget(self.create_vpn_tabs)
        left_pane.addWidget(self.create_vpn_btn)

        two_pane_layout = QHBoxLayout()
        two_pane_layout.addLayout(left_pane)
        two_pane_layout.addWidget(self.vline)
        two_pane_layout.addLayout(self.vpn_connect_section)

        main_layout.addLayout(two_pane_layout)
        main_layout.addWidget(self.hline)
        main_layout.addWidget(self.status)

        self.setCentralWidget(main_widget)

    def main_window_set_admin_layout(self):
        """Set the dashboard user layout.
    
        Hides guest user layout as we will only be connecting with one user.
        The user will see the username/obfuscated password they entered.
        """
        self.username_textfield.setText(
            self.login_dict['username'])
        self.username_textfield.setReadOnly(True)
        self.password_textfield.setText(
            self.login_dict['password'])
        self.password_textfield.setReadOnly(True)

    def main_window_set_guest_layout(self):
        """Set the guest user layout.
    
        Hides dashboard user layout as we will only be connecting with one user.
        The user will see blank user/pass text fields where they can enter
        information for a guest user.
        """
        self.radio_username_textfield.clear()
        self.radio_username_textfield.setReadOnly(False)
        self.radio_password_textfield.clear()
        self.radio_password_textfield.setReadOnly(False)

    @staticmethod
    def add_all_to_layout(layout, element_list):
        """Add all of the elements to the layout."""
        for elem in element_list:
            if isinstance(elem, QWidget):
                layout.addWidget(elem)
            elif is_layout(elem):
                layout.addLayout(elem)
            elif isinstance(elem, QSpacerItem):
                layout.addItem(elem)
            else:
                print("ERROR: Trying to add illegal element to UI!")
                exit(1)
