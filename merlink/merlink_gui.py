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

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QDialog

from merlink.browsers.dashboard import DashboardBrowser
from merlink.browsers.client_vpn import ClientVpnBrowser
from merlink import main_window_ui as guify
from merlink.vpn.vpn_connection import VpnConnection


class LoginDialog(QDialog):
    """This class provides dialog GUI elements.

    Attributes:
        browser (MechanicalSoup): A browser in which to store user credentials.

    """

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
        guify.LoginWindowUi(self)

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
        result = self.browser.login(username, password)

        if result == 'auth_error':
            guify.show_error_dialog('ERROR: Invalid username or password.')
            self.password_field.setText('')
        elif result == 'sms_auth':
            self.tfa_dialog_setup()
        elif result == 'auth_success':
            self.login_dict['username'] = username
            self.login_dict['password'] = password
            self.close()
        elif result == 'ConnectionError':
            guify.show_error_dialog("""ERROR: No internet
            connection!\n\nAccess to
                the internet is required for MerLink to work. Please check
                your network settings and try again. Now exiting...""")
            sys.exit()
        else:
            guify.show_error_dialog("ERROR: Invalid authentication type!")

    def tfa_dialog_setup(self):
        """Create and execute the UI for the TFA dialog."""
        # Create dialog window with login window object
        guify.TfaDialogUi(self)

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
            guify.show_error_dialog('ERROR: Invalid verification code!')


class MainWindow(QMainWindow):
    """Main Window is the controlling class for the GUI.

    Attributes:
        browser (ClientVpnBrowser): Browser used to store user credentials
        menu_widget (MenuBarsUi): Used to tie the menu bars to the MainWindow
        tray_icon (SystrayIconUi): Used to tie the tray icon to the MainWindow

    """

    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self):
        """Initialize GUI objects, decorate main window object, and show it."""
        super(MainWindow, self).__init__()
        self.browser = ClientVpnBrowser()

        # Tie the menu bars, tray_icon, and main window UI to this object.
        self.menu_widget = guify.MenuBarsUi(self.menuBar())
        self.menu_widget.generate_menu_bars()
        self.tray_icon = guify.SystrayIconUi(self)
        self.login_dict = {'username': '', 'password': ''}
        self.main_window = guify.MainWindowUi(self)

        self.show()

    def attempt_login(self):
        """Create a LoginDialog object and steal its cookies."""
        # Make main window grayed out while user logs in
        self.setEnabled(False)
        login_dialog = LoginDialog()
        login_dialog.exec_()
        self.browser.browser = login_dialog.browser.browser
        self.browser.active_org_id = login_dialog.browser.active_org_id
        self.browser.active_network_id = \
            login_dialog.browser.active_network_id
        self.browser.orgs_dict = login_dialog.browser.orgs_dict
        self.login_dict = login_dialog.login_dict
        self.setEnabled(True)

    def init_ui(self):
        """Show the main menu GUI.

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
        self.main_window.main_window_set_admin_layout()
        self.radio_admin_user.toggled.connect(
            self.main_window.main_window_set_admin_layout)
        self.radio_guest_user.toggled.connect(
            self.main_window.main_window_set_guest_layout)

        org_list = self.browser.get_org_names()
        self.org_dropdown.addItems(org_list)
        # Get the data we need and remove the cruft we don't
        current_org = self.browser.get_active_org_name()
        print('main window orgs', org_list)
        self.status.showMessage("Status: Fetching networks in " + current_org +
                                "...")
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
        """Change the org by getting required data and showing it to user.

        * If we don't have data for this org, get info; otherwise don't.
        * If the user has not selected an organization, this fn will do naught.
        """
        # -1 due to having a 'select' option.
        selected_org_index = self.org_dropdown.currentIndex() - 1
        selected_org_name = self.org_dropdown.currentText()
        self.connect_btn.setEnabled(False)
        self.vpn_name_textfield.setEnabled(False)
        if selected_org_index == -1:
            self.status.showMessage("Status: Select an Organization")
            self.network_dropdown.setEnabled(False)
        else:
            self.network_dropdown.setEnabled(True)
            self.status.showMessage("Status: Fetching organizations...")
            # Change primary organization
            self.browser.set_org_name(selected_org_name)
            print("In change_organization and this is the network list " +
                  str(self.browser.get_network_names(['wired'])))

            self.refresh_network_dropdown()
            self.status.showMessage("Status: In org " +
                                    self.browser.get_active_org_name())

    def change_network(self):
        """Change the network to new value for both model and view.

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
            network_list = self.browser.get_network_names(['wired'])
            print('main window network list', network_list)
            current_network = network_list[current_network_index]
            self.status.showMessage("Status: Fetching network data for " +
                                    current_network + "...")

            self.browser.set_network_name(current_network, 'wired')
            print('current_network', current_network)
            self.browser.get_client_vpn_data()
            if not self.browser.is_client_vpn_enabled():
                self.connect_btn.setEnabled(False)
                self.vpn_name_textfield.setEnabled(False)
                error_message = "ERROR: Client VPN is not enabled on " + \
                                current_network + ".\n\nPlease enable it and"\
                                + " try again."
                guify.show_error_dialog(error_message)
                self.status.showMessage("Status: Client VPN is not enabled on "
                                        "'" + current_network + "'. Please "
                                        "enable it and try again.")
            else:
                self.connect_btn.setEnabled(True)
                self.status.showMessage("Status: Ready to connect to " +
                                        current_network + ".")
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

        current_org_network_list = self.browser.get_network_names(['wired'])
        print('current_org_network_list', current_org_network_list)
        self.network_dropdown.addItems(current_org_network_list)

    def setup_vpn(self):
        """Set up VPN vars and start OS-dependent connection scripts.

        Pass vpn vars that are required for an L2TP connection as
        list vpn_data. Pass OS-specific parameters as list <OS>_options.
        """
        # If they have not selected organization or network
        if 'Select' in self.org_dropdown.currentText() or \
                'Select' in self.network_dropdown.currentText():
            # They haven't selected an item in one of the message boxes
            self.show_error_dialog('You must select BOTH an organization '
                                   'AND network before connecting!')

        else:
            self.status.showMessage('Status: Connecting...')
            connection = VpnConnection(vpn_data=self.get_vpn_data(),
                                       vpn_options=self.get_vpn_options())

            return_code = connection.attempt_vpn()
            successful_connection = (return_code == 0)
            if successful_connection:
                self.communicate_vpn_success()
            else:
                self.communicate_vpn_failure()

    def get_vpn_data(self):
        """Gather the VPN data from various sources."""
        # If the user is logging in as a guest user
        if self.radio_admin_user.isChecked() == 0:
            username = self.radio_username_textfield.text()
            password = self.radio_password_textfield.text()
        else:
            username = self.login_dict['username']
            password = self.login_dict['password']

        vpn_name = self.vpn_name_textfield.text()
        address = self.browser.get_client_vpn_address()
        psk = self.browser.get_client_vpn_psk()
        return [vpn_name, address, psk, username, password]

    def get_vpn_options(self):
        """Return with vpn options."""
        vpn_options = [
            self.dns_suffix_txtbox.text(),
            self.idle_disconnect_spinbox.value(),
            self.split_tunneled_chkbox.checkState(),
            self.remember_credential_chkbox.checkState(),
            self.use_winlogon_chkbox.checkState(),
            1,
        ]
        return vpn_options

    def communicate_vpn_success(self):
        """Let the user know that they are connected."""
        self.status.showMessage('Status: Connected')
        guify.vpn_status_dialog("Connection Success",
                                "Successfully Connected!")

        # Show this when connected
        self.tray_icon.set_vpn_success()
        self.status.showMessage("Status: Connected to " +
                                self.network_dropdown.currentText() + ".")
        self.hide()

    def communicate_vpn_failure(self):
        """Let the user know that the VPN connection failed."""
        self.status.showMessage('Status: Connection Failed')
        guify.show_error_dialog("Connection Failure")
        self.tray_icon.set_vpn_failure()

        self.status.showMessage("Status: Connection failed to " +
                                self.network_dropdown.currentText() + ".")
        # Show user error text if available
        guify.show_error_dialog(self.browser.troubleshoot_client_vpn())
