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
import time

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QHeaderView
from PyQt5.Qt import QSizePolicy, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor

from merlink.qt.gui_utils import disable_lineedit
from merlink.os_utils import list_vpns


def is_layout(obj):
    """Check whether the object is a layout of one type."""
    return isinstance(obj, QHBoxLayout) or isinstance(obj, QVBoxLayout)


class MainWindowUi(QMainWindow):
    """This class manages the system tray icon of the main program, post-login.
    """

    def __init__(self):
        super(QMainWindow, self).__init__()
        # Using a StackedWidget to be able to replace login window
        # https://stackoverflow.com/questions/13550076
        self.cw = QWidget()
        # Set minimum width of Main Window to 800 pixels
        self.cw.setMinimumWidth(800)
        self.setWindowTitle('Merlink - VPN Client for Meraki firewalls')
        self.link_style = "font-family: verdana, sans-serif; font-style:" \
                          " normal; font-size: 13px; color: #1795E6;"

        # Required for Login. Elements should be object variables if they
        # Could be called by other modules
        self.login_dict = {}
        self.dashboard_username_field = QLineEdit()
        self.dashboard_password_field = QLineEdit()
        self.guest_user_chkbox = QCheckBox("Use different account.")
        self.dashboard_password_field.setEchoMode(QLineEdit.Password)
        self.org_dropdown = QComboBox()
        self.create_vpn_btn = QPushButton("Create VPN Interface")
        self.org_dropdown = QComboBox()
        self.network_dropdown = QComboBox()
        self.idle_disconnect_chkbox = QCheckBox("Idle disconnect seconds?")
        self.idle_disconnect_spinbox = QSpinBox()
        # Problems will be populated by merlink_gui.py
        self.potential_problem_list = QListWidget()
        self.connect_vpn_btn = QPushButton("Connect")

        self.hline = QFrame()
        self.vline = QFrame()
        self.status = QStatusBar()
        self.vpn_name_textfield = QLineEdit()
        self.vpn_connect_widget = QWidget()

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
        self.refresh_problem_list_view()

        self.decorate_sections()
        self.combine_sections_dashboard()

        # Set the layout once we are done adding elements
        self.main_window_set_admin_layout()
        self.show()

    def setup_dashboard_tab(self):
        """Provide input fields for dashboard-gathered data."""
        # Allows us to replace dashboard login (if successful) with elements
        # that depend upon it (org names, network names, etc.)
        self.tab_dashboard.layout = QVBoxLayout()
        """
        login_ui = QVBoxLayout()
        login_checkbox = QCheckBox("sample label")
        login_ui.addWidget(self.login_checkbox)
        self.tab_dashboard.setLayout(self.login_ui)
        dashboard_tab_stack = QStackedLayout()
        dashboard_tab_stack.addWidget
        """

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
                self.dashboard_username_field,
                password_label,
                self.dashboard_password_field,
                self.org_dropdown,
                self.network_dropdown
            ]
        )
        self.tab_dashboard.layout.addWidget(self.guest_user_chkbox)
        self.tab_dashboard.layout.addLayout(email_pass_layout)
        self.tab_dashboard.setLayout(self.tab_dashboard.layout)

    def disable_email_pass(self, change_to_disabled):
        """Disable username/password if user should not edit them."""
        disable_lineedit(self.dashboard_username_field, change_to_disabled)
        disable_lineedit(self.dashboard_password_field, change_to_disabled)
        if change_to_disabled:
            self.main_window_set_admin_layout()
        else:
            self.main_window_set_guest_layout()

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
                vpn_name_layout,
                QLabel("<h4>VPN Options (Windows only)</h4>"),
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
        self.manual_username_textfield = QLineEdit()
        self.manual_password_textfield = QLineEdit()
        self.manual_password_textfield.setEchoMode(QLineEdit.Password)
        username_label = QLabel("Email")
        password_label = QLabel("Password")
        server_name_label = QLabel("Server name/IP")
        self.manual_server_name_textfield = QLineEdit()
        shared_secret_label = QLabel("Shared Secret")
        self.manual_shared_secret_textfield = QLineEdit()
        self.manual_shared_secret_textfield.setEchoMode(QLineEdit.Password)
        self.add_all_to_layout(
            self.tab_manual.layout,
            [
                username_label,
                self.manual_username_textfield,
                password_label,
                self.manual_password_textfield,
                server_name_label,
                self.manual_server_name_textfield,
                shared_secret_label,
                self.manual_shared_secret_textfield,
                QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
            ]
        )
        self.tab_manual.setLayout(self.tab_manual.layout)

    def vpn_connect_setup(self):
        """Setup the GUI componentst of the right pane."""
        vpn_connect_section = QVBoxLayout(self.vpn_connect_widget)
        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)
        vpn_data = list_vpns()
        vpn_list = QTreeWidget()
        # Last Attempted should have unicode X or V, depending.
        # Ideographic CJK space added to end of headers for spacing
        local_tz = time.localtime().tm_zone
        headers = [
            "VPN Name　",
            "Last Attempt　",
            "Server　",
            "Username　"
        ]
        vpn_list.setHeaderLabels(headers)
        vpn_list.setUniformRowHeights(True)
        vpn_list.setAlternatingRowColors(True)
        # Resize all headers
        for i in range(4):
            vpn_list.header().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        for connection in vpn_data:
            if vpn_data[connection]["is_connected"]:
                state = "Is Connected"
            elif vpn_data[connection]["last_connected"] == "Never":
                state = "Never"
            elif vpn_data[connection]["last_attempted"] != "Never" and \
                    vpn_data[connection]["last_connected"] == vpn_data[connection]["last_attempted"]:
                state = "Succeeded"
            else:
                state = "Failed"

            name = vpn_data[connection]["name"]
            print(name + ' data:', vpn_data[connection])
            this_widget = QTreeWidgetItem(vpn_list, [
                name,
                state,
                vpn_data[connection]["CommRemoteAddress"],
                vpn_data[connection]["AuthName"]
            ])
            # Make it so table entries are selectable (and can be copied)
            # Editable is a side effect (doesn't actually change anything)
            this_widget.setFlags(this_widget.flags() | Qt.ItemIsEditable)

            verbose_data = QTreeWidgetItem(this_widget, ["Verbose OS Data"])
            last_connected_node = QTreeWidgetItem(
                this_widget,
                ["Last Connected",
                 vpn_data[connection]["last_connected"] + " (" + local_tz + ")"]
            )
            last_attempted_node = QTreeWidgetItem(
                this_widget,
                ["Last Attempted",
                 vpn_data[connection]["last_attempted"] + " (" + local_tz + ")"]
            )
            last_connected_node.setFlags(last_connected_node.flags() | Qt.ItemIsEditable)
            last_attempted_node.setFlags(last_attempted_node.flags() | Qt.ItemIsEditable)
            for key in vpn_data[connection]:
                value = str(vpn_data[connection][key])
                # If the first letter is uppercase, it's data from the OS.
                if key[0].isupper():
                    _child_widget = QTreeWidgetItem(verbose_data, [key, value])
                elif key[0] == 'b' or key[0] == 'v':
                    key = ' '.join([word.capitalize() for word in key.split('_')])
                    _child_widget = QTreeWidgetItem(last_connected_node, [key, value])
                elif not key.startswith('last'):  # last_connected/last_attempted taken care of above
                    key = key.replace('_', ' ').capitalize()
                    _child_widget = QTreeWidgetItem(this_widget, [key, value])
                _child_widget.setFlags(_child_widget.flags() | Qt.ItemIsEditable)

        interface_details = QPlainTextEdit()
        interface_details.setReadOnly(True)
        # Check for problems if attempted time > connection time or connection time DNE
        self.add_all_to_layout(
            vpn_connect_section,
            [
                QLabel("<h3>VPN Connections</h3>"),
                hline,
                QLabel("<h4>VPN List</h4>"),
                vpn_list,
                QLabel("<h4>Preflight Checklist</h4>"),
                QLabel("<p><i>Runs when the last attempt for this connection was unsuccessful.</i></p>"),
                self.potential_problem_list,
                self.connect_vpn_btn
            ]
        )

    def refresh_problem_list_view(self, success_checks=None):
        """Refresh the problem list view. Provides a method merlink_gui can call.
        The reason a QListWidget is used here instead of a QPlainTextEdit is that
        it is easier to add icons to a QListWidget (and then make it unselectable).
        """
        # If this is run without sending in data, use unknown icon
        successes_unknown = success_checks is None
        check_texts = [
            "1. Is the user behind the firewall?",
            "2. Is there a firewall in the network?",
            "3. Is the firewall online?",
            "4. Is 500 + 4500 traffic being forwarded?",
            "5. Is 500 + 4500 traffic being natted?",
            "6. Can the client ping the firewall?"
        ]

        # Delete existing and refresh
        self.potential_problem_list.clear()
        for i in range(6):
            if successes_unknown:
                icon = QIcon("media/question-mark-16.png")
            elif success_checks[i]:
                icon = QIcon("media/checkmark-16.png")
            else:
                icon = QIcon("media/x-mark-16.png")
            widget_item = QListWidgetItem(icon, check_texts[i])
            if successes_unknown:
                widget_item.setForeground(QBrush(QColor("#aaaaaa")))
            widget_item.setFlags(widget_item.flags() & ~Qt.ItemIsSelectable)
            self.potential_problem_list.addItem(widget_item)

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
        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)
        # Status bar be at bottom and inform user of what the program is doing.
        self.status.showMessage("Status: -")
        self.status.setStyleSheet("Background:#fff")

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        left_pane_widget = QWidget()
        left_pane = QVBoxLayout(left_pane_widget)
        left_pane.addWidget(QLabel("<h3>Create VPN Connection</h3>"))
        left_pane.addWidget(hline)
        left_pane.addWidget(self.create_vpn_tabs)
        left_pane.addLayout(self.vpn_opts_layout)
        # Ensure that create vpn button is on bottom
        left_pane.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        left_pane.addWidget(self.create_vpn_btn)
        # Nothing in the left pane should need to be expanded horizontally
        left_pane_widget.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))

        two_pane_layout = QHBoxLayout()
        two_pane_layout.addWidget(left_pane_widget)
        two_pane_layout.addWidget(self.vline)
        two_pane_layout.addWidget(self.vpn_connect_widget)

        main_layout.addLayout(two_pane_layout)
        main_layout.addWidget(self.hline)
        main_layout.addWidget(self.status)

        self.setCentralWidget(main_widget)

    def main_window_set_admin_layout(self):
        """Set the dashboard user layout.
    
        Hides guest user layout as we will only be connecting with one user.
        The user will see the username/obfuscated password they entered.
        """
        self.dashboard_username_field.setText(
            self.login_dict['username'])
        self.dashboard_username_field.setReadOnly(True)
        self.dashboard_password_field.setText(
            self.login_dict['password'])
        self.dashboard_password_field.setReadOnly(True)

    def main_window_set_guest_layout(self):
        """Set the guest user layout.
    
        Hides dashboard user layout as we will only be connecting with one user.
        The user will see blank user/pass text fields where they can enter
        information for a guest user.
        """
        self.dashboard_username_field.clear()
        self.dashboard_username_field.setReadOnly(False)
        self.dashboard_password_field.clear()
        self.dashboard_password_field.setReadOnly(False)

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
