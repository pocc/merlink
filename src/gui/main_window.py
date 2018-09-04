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

from src.gui.modal_dialogs import show_error_dialog, vpn_success_dialog
from src.modules.dashboard_browser import DataScraper
from src.modules.vpn_connection import VpnConnection
from src.modules.vpn_tests import TroubleshootVpn
from src.modules.os_utils import is_duplicate_application
from src.gui.menu_bars import MenuBars
import src.gui.gui_setup as gui_setup
from src.gui.systray import SystrayIcon
from src.gui.tshoot_failed_vpn_dialog import tshoot_failed_vpn_dialog

DEBUG = True


class MainWindow(QMainWindow):
    """Main Window is the controlling class for the GUI.

    Attributes:
        browser (DataScraper): Browser used to store user credentials
        menu_widget (MenuBars): Used to tie the menu bars to the MainWindow
        tray_icon (SystrayIcon): Used to tie the tray icon to the MainWindow
    """
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self):
        super(MainWindow, self).__init__()
        # If there's  a duplicate instance, close this one
        if is_duplicate_application('merlink'):
            show_error_dialog('ERROR: You already have a running merlink '
                              'instance!\nThis application will now close.')
            self.close()  # In lieu of sys.exit(app.exec_())

        self.browser = DataScraper()
        self.dropdown_org_index = 0
        self.dropdown_network_index = 0

        # Tie the menu bars, tray_icon, and main window UI to this object.
        self.menu_widget = MenuBars(self.menuBar())
        self.menu_widget.generate_menu_bars()
        self.tray_icon = SystrayIcon(self)
        gui_setup.main_window_widget_setup(self)
        gui_setup.main_window_set_layout(self)

        self.show()

    def show_main_menu(self):
        """Show the main menu GUI

        ~ will be called on main_window instantiation. Creates the
        scaffolding for the main menu GUI and generates all GUI elements
        that will be later used by other class methods.

        ~ has three Qt signals/slots :
            * Organization dropdown changed -> Update model and view
            * Network dropdown changed -> Update model and view
            * "Connect" button clicked -> Initiate VPN connection

        """
        # Set up radio button for dashboard/admin user
        gui_setup.main_window_set_admin_layout(self)
        self.radio_admin_user.toggled.connect(self.set_admin_layout)
        self.radio_guest_user.toggled.connect(self.set_guest_layout)

        org_list = self.browser.get_org_names()
        self.org_dropdown.addItems(org_list)
        # Get the data we need and remove the cruft we don't
        current_org = org_list[self.browser.get_active_org_index()]
        print('main window orgs', org_list)
        self.status.showMessage("Status: Fetching networks in " +
                                current_org + "...")
        # Remove all elements from the network UI dropdown
        self.network_dropdown.clear()
        self.refresh_network_dropdown()

        # All of the major MainWindow slots that signals target
        self.org_dropdown.currentIndexChanged.connect(self.change_organization)
        self.network_dropdown.activated.connect(self.change_network)
        self.connect_btn.clicked.connect(self.setup_vpn)

    def change_organization(self):
        """Change the org by getting required data and showing it to user

        * If the user has not selected an organization, this fn will do nothing.
        * If we already have the network data for this org, then don't scrape
          it with the browser; otherwise do.
        * Regardless, update the network dropdown with new values
          and let the user know to select one of the networks
        """

        self.network_dropdown.setEnabled(True)
        self.status.showMessage("Status: Fetching organizations...")
        # Change primary organization
        """
        If the organization index of network_list is empty (i.e. this 
        network list for this org has never been updated), then get the
        networks for this organization. This makes it so we don't need 
        to get the network list twice for the same organization
        """
        selected_org_index = self.org_dropdown.currentIndex() - 1
        self.browser.set_active_org_index(selected_org_index)
        print("In change_organization and this is the network list "
              + str(self.browser.get_active_org_networks()))

        self.refresh_network_dropdown()
        self.status.showMessage("Status: In org " +
                                self.browser.get_active_org_name())

    def change_network(self):
        """Change the network to new value for both model and view

        This will have been triggered by a network dropdown change. Get
        network info for this network and let user know.
        """

        current_network_index = self.network_dropdown.currentIndex()
        network_list = self.browser.get_active_org_networks()
        print('main window network list', network_list)
        current_network = network_list[current_network_index]
        self.status.showMessage("Status: Fetching network data for "
                                + current_network + "...")

        self.browser.scrape_network_vars(current_network_index)
        self.status.showMessage("Status: Ready to connect to "
                                + current_network + ".")

    def refresh_network_dropdown(self):
        """Remove old values of the network dropdown and add new ones.

        Remove previous contents of Networks QComboBox and
        add new ones according to chosen organization
        """
        self.network_dropdown.clear()

        current_org_network_list = self.browser.get_active_org_networks()
        print('current_org_network_list', current_org_network_list)
        self.network_dropdown.addItems(current_org_network_list)

    def tshoot_vpn_fail_gui(self):
        """Troubleshoot VPN failure and then show the user the results."""
        result = TroubleshootVpn(self.fw_status_text,
                                 self.client_vpn_text,
                                 self.current_ddns,
                                 self.current_primary_ip)
        tshoot_failed_vpn_dialog(result.get_test_results())
        self.status.showMessage("Status: Ready to connect to "
                                + self.current_network + ".")

    def close_window(self):
        """Closes the window object."""
        self.close()

    def setup_vpn(self):
        """Setup VPN vars and start OS-dependent connection scripts"""
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
            network_name = self.network_dropdown.currentText()
            # Set VPN name to the network name +/- cosmetic things
            vpn_name = network_name.replace('- appliance', '') + '- VPN'

            # If the user is logging in as a guest user
            if self.radio_dashboard_admin_user.isChecked() == 0:
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
                vpn_name,
                self.browser.get_vpn_var('psk'),
                self.browser.get_vpn_var('ddns'),
                self.browser.get_vpn_var('ip'),
                username,
                password
            ]
            connection = VpnConnection(vpn_data)

            if sys.platform == 'win32':
                windows_options = [
                    self.dns_suffix_txtbox.text(),
                    self.idle_disconnect_spinbox.value(),
                    self.split_tunneled_chkbox.checkState(),
                    self.remember_credential_chkbox.checkState(),
                    self.use_winlogon_chkbox.checkState(),
                    DEBUG,
                ]
                return_code = \
                    connection.attempt_windows_vpn(windows_options)

            elif sys.platform == 'darwin':
                macos_options = []
                return_code = \
                    connection.attempt_macos_vpn(macos_options)

            # linux, linux2 are valid for linux distros
            elif sys.platform.startswith('linux'):
                linux_options = []
                return_code = \
                    connection.attempt_linux_vpn(linux_options)

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
        vpn_success_dialog()

        # Show this when connected
        self.tray_icon.set_vpn_success()

        self.hide()

    def communicate_vpn_failure(self):
        """Let the user know tha the VPN connection failed."""
        self.status.showMessage('Status: Connection Failed')
        self.error_dialog("Connection Failed")
        self.tray_icon.set_vpn_failure()
        self.troubleshoot_connection()

    def troubleshoot_connection(self):
        """TODO: Stand-in for a function that will troubleshoot after failure"""
        print("ACTIVELY troubleshooting connection")
        show_error_dialog('VPN Connection Failed!')
        self.status.showMessage("Status: Verifying configuration for "
                                + self.current_network + "...")

    def is_vpn_connected(self):
        """Determines whether the VPN is connected.

        TODO: Implement this function

        Returns:
             vpn_status (bool): Whether or not there is an active VPN connection
        """
        vpn_status = False
        return vpn_status

    def set_admin_layout(self):
        """Set the dashboard admin layout."""
        gui_setup.main_window_set_admin_layout(self)

    def set_guest_layout(self):
        """Set the guest user layout."""
        gui_setup.main_window_set_guest_layout(self)
