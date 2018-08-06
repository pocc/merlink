# Python libraries
import sys
from PyQt5.QtWidgets import QMainWindow
import subprocess
from os import getcwd, system

# Import the login_window file
from src.gui.modal_dialogs import show_error_dialog, vpn_success_dialog
from src.modules.dashboard_browser import DataScraper
from src.modules.vpn_connection import VpnConnection
from src.modules.troubleshoot_vpn_failure import TroubleshootVpnFailure
from src.gui.menu_bars import MenuBars
from src.gui.main_window_ui import MainWindowUi
from src.gui.systray import SystrayIcon
from src.gui.tshoot_failed_vpn_dialog import tshoot_failed_vpn_dialog

DEBUG = True


class MainWindow(QMainWindow):
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self):
        super(MainWindow, self).__init__()

        if DEBUG:
            print("Main Window")

        """
        # Shelving this code as it prevents multiple processes using an IDE 
        if is_online():
            error_dialog('ERROR: You already have a running merlink instance!'
                         '\nThis application will now close.')
            self.close()  # In lieu of sys.exit(app.exec_())
        """

        # Passing the self.menuBar() variable is critical for menu bars
        self.menu_widget = MenuBars(self.menuBar())
        self.menu_widget.generate_menu_bars()

        # Variables
        self.browser = DataScraper()
        self.platform = sys.platform
        self.network_admin_only = False
        # We use cwd in multiple places, so fetch current working dir once
        self.cwd = getcwd()
        self.tray_icon = SystrayIcon(self)
        self.is_connected = False

        self.main_window_ui = MainWindowUi(self)
        self.show()

    def show_main_menu(self):
        # Set entered dashboard email/redacted password to be shown by default
        self.main_window_ui.set_dashboard_user_layout()

        org_list = self.browser.get_org_list()
        current_org = self.browser.get_current_org()
        self.org_dropdown.addItems(org_list)
        # Get the data we need and remove the cruft we don't
        self.browser.scrape_org_networks()
        self.status.showMessage("Status: Fetching networks in " +
                                current_org + "...")
        # Remove all elements from the network UI dropdown
        self.network_dropdown.clear()
        self.refresh_network_dropdown()

        # When we have the organization, we can scrape networks
        # When the user changes the organization dropdown, call the scrap
        # networks method. Only change organization when there are more than 1
        # organization to change

        # We don't need to change organization if the user chooses
        # "-- Select an Organization --"

        self.org_dropdown.currentIndexChanged.connect(self.change_organization)
        self.network_dropdown.activated.connect(self.change_network)

        self.connect_btn.clicked.connect(self.connect_vpn)

    def change_organization(self):
        # We only care if they've actually selected an organization
        if self.org_dropdown.currentIndex() != 0:
            self.network_dropdown.setEnabled(True)
            self.status.showMessage("Status: Fetching organizations...")
            # Change primary organization
            selected_org = self.org_dropdown.currentText()
            """
            If the organization index of network_list is empty (i.e. this 
            network list for this org has never been updated), then get the
            networks for this organization. This makes it so we don't need 
            to get the network list twice for the same organization
            """
            # -1 accounting for first option being -- Select --
            selected_org_index = self.org_dropdown.currentIndex() - 1
            print("In change_organization and this is network list "
                  + str(self.browser.get_org_networks()))
            # If we have network data for the selected org
            selected_org_networks = self.browser.org_has_networks(
                selected_org_index)
            # [] == False, so any content means we have networks for that org
            # If we've already scraped networks for that org, do nothing
            if selected_org_networks:
                print("we already have that info for " + selected_org +
                      " at index" + str(selected_org_index))
            else:
                print("getting networks from change_organization")
                print("we are getting new info for " + selected_org +
                      " at index" + str(selected_org_index))
                self.browser.set_current_org(selected_org_index)
                self.browser.scrape_org_networks()

            self.refresh_network_dropdown()
            self.status.showMessage("Status: Select network")

    def change_network(self):
        # Because dropdown has first option 'select'
        current_network_index = self.network_dropdown.currentIndex()-1
        network_list = self.browser.get_org_networks()
        current_network = network_list[current_network_index]
        self.status.showMessage("Status: Fetching network data for "
                                + current_network + "...")

        self.browser.scrape_network_vars(current_network_index)

    def refresh_network_dropdown(self):
        # Remove previous contents of Networks QComboBox and
        # add new ones according to chosen organization
        self.network_dropdown.clear()
        self.network_dropdown.addItems(["-- Select a Network --"])

        current_org_network_list = self.browser.get_org_networks()
        self.network_dropdown.addItems(current_org_network_list)

    def tshoot_vpn_fail_gui(self):
        result = \
            TroubleshootVpnFailure(self.fw_status_text, self.client_vpn_text,
                                   self.current_ddns, self.current_primary_ip)
        tshoot_failed_vpn_dialog(result.get_test_results())
        self.status.showMessage("Status: Ready to connect to "
                                + self.current_network + ".")

    def close_window(self):
        self.close()

    def closeEvent(self, event):
        event.ignore()
        # Show the user the message so they know where the program went
        self.tray_icon.application_minimized()

        self.showMinimized()

    def connect_vpn(self):
        if DEBUG:
            print("entering attempt_connection function")
        # If they've selected organization and network
        if 'Select' not in self.org_dropdown.currentText() and \
                'Select' not in self.network_dropdown.currentText():
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
                self.browser.current_ddns,
                self.browser.psk,
                username,
                password
            ]
            connection = VpnConnection(vpn_data)

            if self.platform == 'win32':
                windows_options = [
                    DEBUG,
                    self.dns_suffix_txtbox.text(),
                    self.idle_disconnect_spinbox.value(),
                    self.split_tunneled_chkbox.checkState(),
                    self.remember_credential_chkbox.checkState(),
                    self.use_winlogon_chkbox.checkState()
                ]
                successful_attempt = \
                    connection.attempt_windows_vpn(windows_options)

            elif self.platform == 'darwin':
                macos_options = []
                successful_attempt = \
                    connection.attempt_macos_vpn(macos_options)

            # linux, linux2 are valid for linux distros
            elif self.platform.startswith('linux'):
                linux_options = []
                successful_attempt = \
                    connection.attempt_linux_vpn(linux_options)

            else:
                successful_attempt = False

            if successful_attempt:
                self.communicate_vpn_success()
            else:
                self.communicate_vpn_failure()

        else:  # They haven't selected an item in one of the message boxes
            self.show_error_dialog('You must select BOTH an organization '
                                   'AND network before connecting!')

    def communicate_vpn_success(self):
        self.is_connected = True
        self.status.showMessage('Status: Connected')
        vpn_success_dialog()

        # Show this when connected
        self.tray_icon.set_vpn_success()

        self.hide()

    def communicate_vpn_failure(self):
        self.is_connected = False
        self.status.showMessage('Status: Connection Failed')
        self.error_dialog("Connection Failed")
        self.tray_icon.set_vpn_failure()
        self.troubleshoot_connection()

    def troubleshoot_connection(self):
        print("ACTIVELY troubleshooting connection")
        show_error_dialog('VPN Connection Failed!')
        self.status.showMessage("Status: Verifying configuration for "
                                + self.current_network + "...")