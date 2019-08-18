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
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt


from merlink.qt.pane_manual_vpn import ManualVpnSetupWidget

def is_layout(obj):
    """Check whether the object is a layout of one type."""
    return isinstance(obj, QHBoxLayout) or isinstance(obj, QVBoxLayout)


class WindowDivUi(QWidget):
    """Window divisions. For example given this window:

    +-----+-----+
    |  1  |  2  |
    +-----+-----+
    |  3  |  4  |
    +-----+-----+

    1, 2, 3, and 4 are "window divs". div ~ HTML div.
    """
    def __init__(self, layout, element_list):
        super(QWidget, self).__init__()
        self.layout = layout
        self.element_list = element_list
        for elem in self.element_list:
            if isinstance(elem, QWidget):
                layout.addWidget(elem)
            elif is_layout(elem):
                layout.addLayout(elem)
            elif isinstance(elem, QSpacerItem):
                layout.addItem(elem)
            else:
                print("ERROR: Trying to add illegal element to UI!")
                exit(1)

    def disable_windiv(self):
        """Disable every element in the window division."""
        self.disable_all_elems(True)

    def enable_windiv(self):
        """Enable every element in the window division."""
        self.disable_all_elems(False)

    def disable_all_elems(self, disable_toggle):
        """Set all elements enabled or disabled."""
        for elem in self.element_list:
            if is_layout(elem):
                for layout_widget in self.layout_widgets(elem):
                    layout_widget.setDisabled(disable_toggle)
            elif not isinstance(elem, QSpacerItem):
                elem.setDisabled(disable_toggle)

    @staticmethod
    def layout_widgets(layout):
        """Return all of the widgets in a layout."""
        count = layout.count()
        widgets = [layout.itemAt(i).widget() for i in range(count)]
        return widgets


class MainWindowUi(QMainWindow):
    """This class manages the system tray icon of the main program, post-login.
    Attributes:
        app (QMainWindow): Set to MainWindow object (required binding for Qt)
    """

    login_section = QVBoxLayout()
    manual_setup_section = QVBoxLayout()
    vpn_opts_section = QVBoxLayout()
    vpn_connect_section = QVBoxLayout()

    login_wd = None
    manual_setup_wd = None
    vpn_opts_wd = None
    vpn_connect_wd = None

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.main_window_widget_setup()

    def setup_window(self):
        # Setup various sections that will be combined
        self.login_setup()
        self.setup_manual_layout()
        self.vpn_opts_setup()
        self.vpn_connect_setup()

        self.decorate_sections()
        self.combine_sections_dashboard()
        # Set the layout once we are done adding elements
        self.main_window_set_admin_layout()

    def setup_dashboard_layout(self):
        """Provide input fields for dashboard-gathered data."""
        self.vpn_opts_wd.enable_windiv()

    def setup_manual_layout(self):
        """Gray out options and provide input fields to manually enter data."""
        username_label = QLabel("Email")
        username_textfield = QLineEdit()
        password_label = QLabel("Password")
        password_textfield = QLineEdit()
        password_textfield.setEchoMode(QLineEdit.Password)
        vpn_name_label = QLabel("VPN Name")
        vpn_name_textfield = QLineEdit()
        server_name_label = QLabel("Server name/IP")
        server_name_textfield = QLineEdit()
        shared_secret_label = QLabel("Shared Secret")
        shared_secret_textfield = QLineEdit()
        shared_secret_textfield.setEchoMode(QLineEdit.Password)
        self.manual_setup_wd = WindowDivUi(
            self.manual_setup_section,
            [
                username_label,
                username_textfield,
                password_label,
                password_textfield,
                vpn_name_label,
                vpn_name_textfield,
                server_name_label,
                server_name_textfield,
                shared_secret_label,
                shared_secret_textfield,
            ])

    def main_window_widget_setup(self):
        """Set up the main window object and org/net dropdowns."""
        # QMainWindow requires that a central app be set
        self.cw = QStackedWidget()
        self.setCentralWidget(self.cw)
        # Set minimum width of Main Window to 500 pixels
        self.cw.setMinimumWidth(500)
        self.setWindowTitle('MerLink - VPN Client for Meraki firewalls')

    def login_setup(self):
        """Set initial vars for user/pass fields for dasboard/guest user."""
        self.username_label = QLabel("Email")
        self.username_textfield = QLineEdit()
        self.password_label = QLabel("Password")
        self.password_textfield = QLineEdit()
        self.password_textfield.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Dashboard Log in")

        self.setup_method_layout = QVBoxLayout()
        self.radio_buttons_layout = QHBoxLayout()
        self.radio_setup_label = QLabel("Setup Method")
        self.radio_setup_label.setAlignment(Qt.AlignCenter)
        self.radio_dashboard_method = QRadioButton("Dashboard")
        self.radio_manual_method = QRadioButton("Manually")
        self.radio_buttons_layout.addWidget(self.radio_dashboard_method)
        self.radio_buttons_layout.addWidget(self.radio_manual_method)
        self.setup_method_layout.addWidget(self.radio_setup_label)
        self.setup_method_layout.addLayout(self.radio_buttons_layout)
        self.radio_setup_method = QGroupBox()
        self.radio_dashboard_method.setChecked(True)
        self.radio_setup_method.setLayout(self.setup_method_layout)
        self.radio_dashboard_method.toggled.connect(
            self.setup_dashboard_layout)
        self.radio_manual_method.toggled.connect(self.combine_sections_manual)

        # Create window division object for login component
        self.login_wd = WindowDivUi(
            self.login_section,
            [
                self.radio_setup_method,
                self.username_label,
                self.username_textfield,
                self.password_label,
                self.password_textfield,
                self.login_btn
            ])

    def manual_setup(self):
        """Setup options for connecting manually if user wants to."""
        self.vpn_opts_wd.setVisible(False)
        #self.manual_setup_wd.

    def vpn_opts_setup(self):
        """Set up the vpn vars UI region."""
        # Create org and network dropdowns so the user can select the firewall
        # they would like to connect to.
        self.org_dropdown = QComboBox()
        self.org_dropdown.addItem('-- Select an Organization --')
        self.network_dropdown = QComboBox()
        self.network_dropdown.setEnabled(False)

        self.radio_user_layout = QHBoxLayout()
        self.radio_user_types = QGroupBox()
        self.radio_admin_user = QRadioButton("Dashboard Admin")
        self.radio_guest_user = QRadioButton("Guest User")
        self.radio_user_layout.addWidget(self.radio_admin_user)
        self.radio_user_layout.addWidget(self.radio_guest_user)
        # Default is to have dashboard user
        self.radio_admin_user.setChecked(True)
        self.radio_user_types.setLayout(self.radio_user_layout)

        # Allow the user to change the VPN name
        self.vpn_name_layout = QHBoxLayout()
        self.vpn_name_label = QLabel("VPN Name:")
        self.vpn_name_textfield = QLineEdit()
        self.vpn_name_layout.addWidget(self.vpn_name_label)
        self.vpn_name_layout.addWidget(self.vpn_name_textfield)
    
        # Ask the user for int/str values if they want to enter them
        self.idle_disconnect_layout = QHBoxLayout()
        self.idle_disconnect_chkbox = QCheckBox("Idle disconnect seconds?")
        self.idle_disconnect_spinbox = QSpinBox()
        self.idle_disconnect_spinbox.setValue(0)
        # Negative seconds aren't useful here
        self.idle_disconnect_spinbox.setMinimum(0)
        self.idle_disconnect_layout.addWidget(
            self.idle_disconnect_chkbox)
        self.idle_disconnect_layout.addWidget(
            self.idle_disconnect_spinbox)
    
        self.dns_suffix_layout = QHBoxLayout()
        self.dns_suffix_chkbox = QCheckBox("DNS Suffix?")
        self.dns_suffix_txtbox = QLineEdit('-')
        self.dns_suffix_layout.addWidget(self.dns_suffix_chkbox)
        self.dns_suffix_layout.addWidget(self.dns_suffix_txtbox)
    
        # Boolean asks of the user
        self.split_tunneled_chkbox = QCheckBox("Split-Tunnel?")
        self.remember_credential_chkbox = QCheckBox("Remember Credentials?")
        self.use_winlogon_chkbox = QCheckBox("Use Windows Logon Credentials?")

        self.create_vpn_btn = QPushButton("Create VPN Interface")

        # Create a horizontal line above the status bar to highlight it
        self.hline = QFrame()
        self.hline.setFrameShape(QFrame.HLine)
        self.hline.setFrameShadow(QFrame.Sunken)

        self.vline = QFrame()
        self.vline.setFrameShape(QFrame.VLine)
        self.vline.setFrameShadow(QFrame.Sunken)
        # Status bar be at bottom and inform user of what the program is doing.
        self.status = QStatusBar()
        self.status.showMessage("Status: -")
        self.status.setStyleSheet("Background:#fff")

        self.vpn_opts_wd = WindowDivUi(
            self.vpn_opts_section,
            [
                self.radio_user_types,
                self.org_dropdown,
                self.network_dropdown,
                self.vpn_name_layout,
                # Add layouts for specialized params
                self.idle_disconnect_layout,
                self.dns_suffix_layout,
                # Add checkboxes
                self.split_tunneled_chkbox,
                self.remember_credential_chkbox,
                self.use_winlogon_chkbox,
                # Ensure that button is at bottom of pane by adding space
                QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding),
                self.create_vpn_btn
            ]
        )

    def vpn_connect_setup(self):
        """Setup the GUI componentst of the right pane."""
        self.vpn_list = QListWidget()
        ipsum_vpn_interfaces = ['eth', 'wifi']
        self.vpn_list.addItems(ipsum_vpn_interfaces)

        self.check_for_probs_cb = QCheckBox(
            "Check for issues before connecting (recommended)")
        self.check_for_probs_cb.setChecked(True)
        self.probs_list = QListWidget()
        problems = ["Forget the milk", "My hovercraft is full of eels"]
        self.probs_list.addItems(problems)
        self.connect_vpn_btn = QPushButton("Connect")

        self.vpn_connect_wd = WindowDivUi(
            self.vpn_connect_section,
            [
                self.vpn_list,
                self.check_for_probs_cb,
                self.probs_list,
                self.connect_vpn_btn
            ]
        )

    def decorate_sections(self):
        """Add a box around each section for readability."""
        # Set GroupBox CSS manually because otherwise margins are huge
        self.setStyleSheet(".QGroupBox {  border: 1px solid #ccc;}")

    def combine_sections_dashboard(self):
        """Combine left and right panes into a final layout."""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        left_pane = QVBoxLayout()
        #self.vpn_opts_wd.setVisible(False)
        left_pane.addLayout(self.login_wd.layout)
        left_pane.addLayout(self.vpn_opts_wd.layout)

        two_pane_layout = QHBoxLayout()
        two_pane_layout.addLayout(left_pane)
        two_pane_layout.addWidget(self.vline)
        two_pane_layout.addLayout(self.vpn_connect_section)

        main_layout.addLayout(two_pane_layout)
        main_layout.addWidget(self.hline)
        main_layout.addWidget(self.status)

        self.cw.addWidget(main_widget)

    def combine_sections_manual(self):
        """Combine left and right panes into a final layout for manual method."""
        second_widget = ManualVpnSetupWidget(self)
        manual_layout = QVBoxLayout(second_widget)

        left_pane = QVBoxLayout()
        #self.vpn_opts_wd.setVisible(False)
        left_pane.addLayout(self.login_wd.layout)

        two_pane_layout = QHBoxLayout()
        two_pane_layout.addLayout(left_pane)
        two_pane_layout.addWidget(self.vline)
        two_pane_layout.addLayout(self.vpn_connect_section)

        manual_layout.addLayout(two_pane_layout)
        manual_layout.addWidget(self.hline)
        manual_layout.addWidget(self.status)

        self.cw.addWidget(second_widget)
        self.cw.setCurrentWidget(second_widget)

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
