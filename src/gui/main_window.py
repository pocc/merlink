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

"""Main Window is the controlling class for the GUI."""
import sys

from PyQt5.QtWidgets import QMainWindow

from src.dashboard_browser.dashboard_browser import DashboardBrowser
from src.gui.menu_bars import MenuBars
from src.gui.login_dialog import LoginDialog
from src.gui.modal_dialogs import show_error_dialog, vpn_status_dialog
from src.gui.systray import SystrayIcon
import src.gui.gui_setup as guify
from src.modules.vpn_connection import VpnConnection

DEBUG = True


class MainWindow(QMainWindow):
    """Main Window is the controlling class for the GUI.

    Attributes:
        browser (DashboardBrowser): Browser used to store user credentials
        menu_widget (MenuBars): Used to tie the menu bars to the MainWindow
        tray_icon (SystrayIcon): Used to tie the tray icon to the MainWindow
    """
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self):
        super(MainWindow, self).__init__()

        self.browser = DashboardBrowser()

        # Tie the menu bars, tray_icon, and main window UI to this object.
        self.menu_widget = MenuBars(self.menuBar())
        self.menu_widget.generate_menu_bars()
        self.tray_icon = SystrayIcon(self)
        guify.main_window_widget_setup(self)
        guify.main_window_set_layout(self)

        self.show()

    def attempt_login(self):
        """Create a LoginDialog object and steal its cookies."""
        # Make main window grayed out while user logs in
        self.setEnabled(False)
        login_dialog = LoginDialog()
        login_dialog.exec_()
        self.browser = login_dialog.browser
        self.setEnabled(True)

    def init_ui(self):
        """Show the main menu GUI

        Is called on main_window instantiation. Creates the
        scaffolding for the main menu GUI and generates all GUI elements
        that will be later used by other class methods.

        Has 2 radio option Qt signals/slots:
            * Admin user radio option toggled -> Set admin user/pass view
            * Guest user radio option toggled -> Set guest user/pass view

        Has 3 program-driving Qt signals/slots:
            * Organization dropdown changed -> Update model and view
            * Network dropdown changed -> Update model and view
            * "Connect" button clicked -> Initiate VPN connection

        """
        # Set up radio button for dashboard/admin user
        guify.main_window_set_admin_layout(self)
        self.radio_admin_user.toggled.connect(self.set_admin_layout)
        self.radio_guest_user.toggled.connect(self.set_guest_layout)

        org_list = self.browser.get_org_names()
        self.org_dropdown.addItems(org_list)
        # Get the data we need and remove the cruft we don't
        current_org = org_list[self.browser.get_active_org_index()]
        print('main window orgs', org_list)
        self.status.showMessage("Status: Fetching networks in " +
                                current_org + "...")
        self.connect_btn.setEnabled(False)
        self.vpn_name_textfield.setEnabled(False)
        # Remove all elements from the network UI dropdown
        self.network_dropdown.clear()
        self.refresh_network_dropdown()

        # All of the major MainWindow slots that signals target
        self.org_dropdown.currentIndexChanged.connect(self.change_organization)
        self.network_dropdown.activated.connect(self.change_network)
        self.connect_btn.clicked.connect(self.setup_vpn)

    def change_organization(self):
        """Change the org by getting required data and showing it to user

        * If we don't have data for this org, get info; otherwise don't.
        * If the user has not selected an organization, this fn will do nothing.
        """
        # -1 due to having a 'select' option.
        selected_org_index = self.org_dropdown.currentIndex() - 1
        self.connect_btn.setEnabled(False)
        self.vpn_name_textfield.setEnabled(False)
        if selected_org_index == -1:
            self.status.showMessage("Status: Select an Organization")
            self.network_dropdown.setEnabled(False)
        else:
            self.network_dropdown.setEnabled(True)
            self.status.showMessage("Status: Fetching organizations...")
            # Change primary organization
            self.browser.set_active_org_index(selected_org_index)
            print("In change_organization and this is the network list "
                  + str(self.browser.get_network_names()))

            self.refresh_network_dropdown()
            self.status.showMessage("Status: In org " +
                                    self.browser.get_active_org_name())

    def change_network(self):
        """Change the network to new value for both model and view

        This will have been triggered by a network dropdown change. Get
        network info for this network and let user know.
        """

        # Off by 1 due to Select option
        current_network_index = self.network_dropdown.currentIndex() - 1
        if current_network_index == -1:
            self.status.showMessage("Status: Select a Network")
            self.connect_btn.setEnabled(False)
            self.vpn_name_textfield.setEnabled(False)
        else:
            network_list = self.browser.get_network_names()
            print('main window network list', network_list)
            current_network = network_list[current_network_index]
            self.status.showMessage("Status: Fetching network data for "
                                    + current_network + "...")

            self.browser.set_active_network_index(current_network_index)

            self.browser.get_client_vpn_data()
            if not self.browser.client_vpn_checks():
                self.connect_btn.setEnabled(False)
                self.vpn_name_textfield.setEnabled(False)
                error_message = "ERROR: Client VPN is not enabled on " + \
                                current_network + ".\n\nPlease enable it and"\
                                + " try again."
                show_error_dialog(error_message)
                self.status.showMessage("Status: Client VPN is not enabled on "
                                        "'" + current_network + "'. Please "
                                        "enable it and try again.")
            else:
                self.connect_btn.setEnabled(True)
                self.status.showMessage("Status: Ready to connect to "
                                        + current_network + ".")
                vpn_name = current_network.replace('- appliance', '') + '- VPN'
                self.vpn_name_textfield.setText(vpn_name)
                self.vpn_name_textfield.setEnabled(True)

    def refresh_network_dropdown(self):
        """Remove old values of the network dropdown and add new ones.

        Remove previous contents of Networks QComboBox and
        add new ones according to chosen organization
        """
        self.network_dropdown.clear()
        self.network_dropdown.addItem('-- Select a Network --')

        current_org_network_list = self.browser.get_network_names()
        print('current_org_network_list', current_org_network_list)
        self.network_dropdown.addItems(current_org_network_list)

    def setup_vpn(self):
        """Setup VPN vars and start OS-dependent connection scripts

        Passes vpn vars that are required for an L2TP connection as
        list vpn_data. Passes OS-specific parameters as list <OS>_options.
        """
        if DEBUG:
            print("entering attempt_connection function")

        # If they have not selected organization or network
        if 'Select' in self.org_dropdown.currentText() or \
                'Select' in self.network_dropdown.currentText():
            # They haven't selected an item in one of the message boxes
            self.show_error_dialog('You must select BOTH an organization '
                                   'AND network before connecting!')

        else:
            # Get current network from dropdown
            # Set VPN name to the network name +/- cosmetic things

            # If the user is logging in as a guest user
            if self.radio_admin_user.isChecked() == 0:
                username = self.radio_username_textfield.text()
                password = self.radio_password_textfield.text()
            else:
                username = self.browser.username
                password = self.browser.password

            # Change status to reflect we're connecting.
            # For fast connections, you might not see this message
            self.status.showMessage('Status: Connecting...')
            # Send a list to attempt_connection containing data
            # from all the textboxes and spinboxes

            # Create VPN connection
            vpn_data = [
                self.vpn_name_textfield.text(),
                self.browser.get_client_vpn_address(),
                self.browser.get_client_vpn_psk(),
                username,
                password
            ]
            print('vpn_data being sent to script: ', vpn_data)
            vpn_options = [
                self.dns_suffix_txtbox.text(),
                self.idle_disconnect_spinbox.value(),
                self.split_tunneled_chkbox.checkState(),
                self.remember_credential_chkbox.checkState(),
                self.use_winlogon_chkbox.checkState(),
                DEBUG,
            ]
            connection = VpnConnection(vpn_data, vpn_options)

            if sys.platform == 'win32':
                return_code = \
                    connection.attempt_windows_vpn()

            elif sys.platform == 'darwin':
                return_code = \
                    connection.attempt_macos_vpn()

            # linux, linux2 are valid for linux distros
            elif sys.platform.startswith('linux'):
                return_code = \
                    connection.attempt_linux_vpn()

            else:
                return_code = False

            successful_connection = (return_code == 0)
            if successful_connection:
                self.communicate_vpn_success()
            else:
                self.communicate_vpn_failure()

    def communicate_vpn_success(self):
        """Let the user know that they are connected."""
        self.status.showMessage('Status: Connected')
        vpn_status_dialog("Connection Success", "Successfully Connected!")

        # Show this when connected
        self.tray_icon.set_vpn_success()

        self.hide()

    def communicate_vpn_failure(self):
        """Let the user know that the VPN connection failed."""
        self.status.showMessage('Status: Connection Failed')
        show_error_dialog("Connection Failure")
        self.tray_icon.set_vpn_failure()

        # Start troubleshooting
        self.status.showMessage("Status: Verifying configuration for "
                                + self.network_dropdown.currentText() + "...")
        self.tshoot_vpn_fail_gui()

    def tshoot_vpn_fail_gui(self):
        """Troubleshoot VPN failure and then show the user the results.

        result = TroubleshootVpn(self.fw_status_text,
                                 self.client_vpn_text,
                                 self.current_ddns,
                                 self.current_primary_ip)
        tshoot_failed_vpn_dialog(result.get_test_results())"""
        self.status.showMessage("Status: Ready to connect to "
                                + self.network_dropdown.currentText() + ".")

    def set_admin_layout(self):
        """Set the dashboard admin layout."""
        guify.main_window_set_admin_layout(self)

    def set_guest_layout(self):
        """Set the guest user layout."""
        guify.main_window_set_guest_layout(self)
