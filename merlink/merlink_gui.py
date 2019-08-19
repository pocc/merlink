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
"""Controlling class for the GUI. Does NOT call Qt classes (see /qt)."""
from merlink.browsers.client_vpn import ClientVpnBrowser
from merlink.qt import main_window
from merlink.qt.pane_login_fullscreen import TfaDialogUi
from merlink.qt.menu_bars import MenuBarsUi
from merlink.qt.system_tray import SystrayIconUi
from merlink.qt.gui_utils import show_error_dialog, vpn_status_dialog
from merlink.vpn.vpn_connection import VpnConnection


class TfaDialog(TfaDialogUi):
    """This class provides dialog GUI elements.
    """
    def __init__(self, app):
        super(TfaDialogUi, self).__init__()
        self.app = app
        self.tfa_success = False

    def tfa_dialog_setup(self):
        """Create and execute the UI for the TFA dialog."""
        # Create dialog window with login window object
        TfaDialogUi(self)

        self.app.yesbutton.clicked.connect(self.tfa_verify)
        self.app.nobutton.clicked.connect(self.app.twofactor_dialog.close)
        while not self.tfa_success:
            self.app.twofactor_dialog.exec_()

    def tfa_verify(self):
        """Submit the tfa code and communicate success/failure to user.

        This fn is partially required because we need a function to connect
        to the button click signal.
        """
        self.tfa_success = self.app.browser.tfa_submit_info(
            self.app.get_twofactor_code.text())
        if self.tfa_success:
            self.app.twofactor_dialog.accept()
        else:
            show_error_dialog('ERROR: Invalid verification code!')


class MainWindow:
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
        self.app = main_window.MainWindowUi()
        self.browser = ClientVpnBrowser()

        # Tie the menu bars, tray_icon, and main window UI to this object.
        self.app.menu_widget = MenuBarsUi(self.app.menuBar())
        self.app.menu_widget.generate_menu_bars()
        self.app.tray_icon = SystrayIconUi(self.app, self)
        self.app.login_dict = {'username': '', 'password': ''}

        # Triggers
        self.app.setup_window()
        self.setup_qt_slots()
        self.app.show()

    def setup_qt_slots(self):
        """Set up pyqt slots for later use by objects.
        All of these objects should have already been created.
        """
        self.app.org_dropdown.currentIndexChanged.connect(
            self.change_organization)
        self.app.main_window_set_admin_layout()
        self.app.guest_user_chkbox.stateChanged.connect(
            lambda state: self.app.disable_email_pass(not state))

    def attempt_login(self):
        """Create a LoginDialog object and steal its cookies."""
        # Make main window grayed out while user logs in
        pass

    def init_vpn_ui(self):
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
        org_list = self.app.browser.get_org_names()
        self.app.org_dropdown.addItems(org_list)
        # Get the data we need and remove the cruft we don't
        current_org = self.app.browser.get_active_org_name()
        print('main window orgs', org_list)
        self.app.status.showMessage("Status: Fetching networks in " + current_org +
                                "...")
        self.app.connect_btn.setEnabled(False)
        self.app.vpn_name_textfield.setEnabled(False)
        # Remove all elements from the network UI dropdown
        self.app.network_dropdown.clear()
        self.app.refresh_network_dropdown()

        # All of the major MainWindow slots that signals target
        self.app.org_dropdown.currentIndexChanged.connect(self.app.change_organization)
        self.app.network_dropdown.activated.connect(self.app.change_network)
        self.app.connect_btn.clicked.connect(self.app.setup_vpn)

    def change_organization(self):
        """Change the org by getting required data and showing it to user.

        * If we don't have data for this org, get info; otherwise don't.
        * If the user has not selected an organization, this fn will do naught.
        """
        # -1 due to having a 'select' option.
        selected_org_index = self.app.org_dropdown.currentIndex() - 1
        selected_org_name = self.app.org_dropdown.currentText()
        self.app.connect_btn.setEnabled(False)
        self.app.vpn_name_textfield.setEnabled(False)
        if selected_org_index == -1:
            self.app.status.showMessage("Status: Select an Organization")
            self.app.network_dropdown.setEnabled(False)
        else:
            self.app.network_dropdown.setEnabled(True)
            self.app.status.showMessage("Status: Fetching organizations...")
            # Change primary organization
            self.app.browser.set_org_name(selected_org_name)
            print("In change_organization and this is the network list " +
                  str(self.app.browser.get_network_names(['wired'])))

            self.app.refresh_network_dropdown()
            self.app.status.showMessage("Status: In org " +
                                    self.app.browser.get_active_org_name())

    def change_network(self):
        """Change the network to new value for both model and view.

        This will have been triggered by a network dropdown change. Get
        network info for this network and let user know.
        """
        # Off by 1 due to Select option
        current_network_index = self.app.network_dropdown.currentIndex() - 1
        if current_network_index == -1:
            self.app.status.showMessage("Status: Select a Network")
            self.app.connect_btn.setEnabled(False)
            self.app.vpn_name_textfield.setEnabled(False)
        else:
            network_list = self.app.browser.get_network_names(['wired'])
            print('main window network list', network_list)
            current_network = network_list[current_network_index]
            self.app.status.showMessage("Status: Fetching network data for " +
                                    current_network + "...")

            # Network name should be unique in an organization.
            self.app.browser.set_network_name(current_network, 'wired')
            print('current_network', current_network)
            self.app.browser.get_client_vpn_data()
            if not self.app.browser.is_client_vpn_enabled():
                self.app.connect_btn.setEnabled(False)
                self.app.vpn_name_textfield.setEnabled(False)
                error_message = "ERROR: Client VPN is not enabled on " + \
                                current_network + ".\n\nPlease enable it and"\
                                + " try again."
                show_error_dialog(error_message)
                self.app.status.showMessage("Status: Client VPN is not enabled on "
                                        "'" + current_network + "'. Please "
                                        "enable it and try again.")
            else:
                self.app.connect_btn.setEnabled(True)
                self.app.status.showMessage("Status: Ready to connect to " +
                                        current_network + ".")
                vpn_name = current_network.replace('- appliance', '') + '- VPN'
                self.app.vpn_name_textfield.setText(vpn_name)
                self.app.vpn_name_textfield.setEnabled(True)

    def refresh_network_dropdown(self):
        """Remove old values of the network dropdown and add new ones.

        Remove previous contents of Networks QComboBox and
        add new ones according to chosen organization
        """
        self.app.network_dropdown.clear()
        self.app.network_dropdown.addItem('-- Select a Network --')

        current_org_network_list = self.app.browser.get_network_names(['wired'])
        print('current_org_network_list', current_org_network_list)
        self.app.network_dropdown.addItems(current_org_network_list)

    def setup_vpn(self):
        """Set up VPN vars and start OS-dependent connection scripts.

        Pass vpn vars that are required for an L2TP connection as
        list vpn_data. Pass OS-specific parameters as list <OS>_options.
        """
        # If they have not selected organization or network
        if 'Select' in self.app.org_dropdown.currentText() or \
                'Select' in self.app.network_dropdown.currentText():
            # They haven't selected an item in one of the message boxes
            self.app.show_error_dialog('You must select BOTH an organization '
                                   'AND network before connecting!')

        else:
            self.app.status.showMessage('Status: Connecting...')
            connection = VpnConnection(vpn_data=self.app.get_vpn_data(),
                                       vpn_options=self.app.get_vpn_options())

            return_code = connection.attempt_vpn()
            successful_connection = (return_code == 0)
            if successful_connection:
                self.app.communicate_vpn_success()
            else:
                self.app.communicate_vpn_failure()

    def get_vpn_data(self):
        """Gather the VPN data from various sources."""
        # If the user is logging in as a guest user
        if self.app.radio_admin_user.isChecked() == 0:
            username = self.app.radio_username_textfield.text()
            password = self.app.radio_password_textfield.text()
        else:
            username = self.app.login_dict['username']
            password = self.app.login_dict['password']

        vpn_name = self.app.vpn_name_textfield.text()
        address = self.app.browser.get_client_vpn_address()
        psk = self.app.browser.get_client_vpn_psk()
        return [vpn_name, address, psk, username, password]

    def get_vpn_options(self):
        """Return with vpn options."""
        vpn_options = [
            self.app.dns_suffix_txtbox.text(),
            self.app.idle_disconnect_spinbox.value(),
            self.app.split_tunneled_chkbox.checkState(),
            self.app.remember_credential_chkbox.checkState(),
            self.app.use_winlogon_chkbox.checkState(),
            1,
        ]
        return vpn_options

    def communicate_vpn_success(self):
        """Let the user know that they are connected."""
        self.app.status.showMessage('Status: Connected')
        vpn_status_dialog("Connection Success", "Successfully Connected!")

        # Show this when connected
        self.app.tray_icon.set_vpn_success()
        self.app.status.showMessage("Status: Connected to " +
                                self.app.network_dropdown.currentText() + ".")
        self.app.hide()

    def communicate_vpn_failure(self):
        """Let the user know that the VPN connection failed."""
        self.app.status.showMessage('Status: Connection Failed')
        show_error_dialog("Connection Failure")
        self.app.tray_icon.set_vpn_failure()

        self.app.status.showMessage("Status: Connection failed to " +
                                self.app.network_dropdown.currentText() + ".")
        # Show user error text if available
        show_error_dialog(self.app.browser.troubleshoot_client_vpn())
