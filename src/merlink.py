#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls

# Build this with './venv/bin/python3 setup.py build' from project root

# Utilities
import sys
import webbrowser

# Qt5
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QSystemTrayIcon, QTextEdit,
                             QVBoxLayout, QComboBox, QMainWindow, QAction, QDialog, QMessageBox,
                             QStatusBar, QFrame, QListWidget, QListWidgetItem, QCheckBox)
from PyQt5.QtGui import QIcon

# Web Scraping
import re
import json
import requests
import bs4

# VPN creation
import subprocess
import platform
from os import getcwd, system

# Import the login_window file
from src.modules.login_window import LoginWindow


class MainWindow(QMainWindow):
    # Pass in browser_session object from LoginWindow so that we can maintain the same session
    # ASSERT: User has logged in and has a connection to Dashboard AND DNS is working
    def __init__(self, browser_session, username, password):
        super(MainWindow, self).__init__()
        if DEBUG:
            print("Main Window")

        # Variables
        self.platform = sys.platform
        self.network_admin_only = False
        self.current_org_index = 0  # By default, we choose the first org to display
        self.org_qty = 0  # By default, you have access to 0 orgs
        # Initialize organization dictionary {Name: Link} and list for easier access. org_list is org_links.keys()
        self.org_links = {}
        self.org_list = []
        self.validation_list = QListWidget()
        self.cwd = getcwd()  # get current working directory. We use cwd in multiple places, so fetch it once

        # QMainWindow requires that a central widget be set
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        # CURRENT minimum width of Main Window - SUBJECT TO CHANGE as features are added
        self.cw.setMinimumWidth(330)

        self.browser = browser_session
        self.username = username
        self.password = password
        self.scrape_orgs()
        self.main_init_ui()
        self.menu_bars()

    # This function will get the organizations and then save them as a dict of names and links
    def scrape_orgs(self):
        """ ASSERTS
        * user is an org admin
        """
        # NOTE: Until you choose an organization, Dashboard will not let you visit pages you should have access to
        page = self.browser.get_current_page()
        # Get a list of all org links
        org_hrefs = page.findAll('a', href=re.compile('/login/org_choose\?eid=.{6}'))
        # Get the number of orgs
        self.org_qty = len(org_hrefs)
        # Create as many network lists in the network list as there are orgs
        self.network_list = [[]] * self.org_qty
        self.base_url_list = [[]] * self.org_qty
        for i in range(self.org_qty):
            org_str = str(org_hrefs[i])
            # 39:-4 = Name, 9:37 = Link
            self.org_links[org_str[39:-4]] = 'https://account.meraki.com' + org_str[9:37]
            self.org_list.append(org_str[39:-4])
            print(org_str[39:-4] + self.org_links[org_str[39:-4]])

    def get_networks(self):
        """ ASSERTS
        * get_networks should only be called on initial startup or if a different organization has been chosen
        * browser should be initialized
        * browser should have clicked on an org in the org selection page so we can browse relative paths of an org
        """
        if DEBUG:
            print("In get_networks")

        self.status.showMessage("Status: Fetching networks in " + self.current_org + "...")

        # If we're dealing with org admins
        if not self.network_admin_only:
            # This method will get the networks by using the administered_orgs json blob
            current_url = self.org_links[self.current_org]
            self.browser.open(current_url)
        current_url = self.browser.get_url()
        # base url is up to '/manage/'
        upper_url_index = current_url.find('/manage')  # boundary between network string and webpage string
        lower_url_index = current_url.find('.com/')  # boundary between domain string and network string
        url_domain_part = current_url[:lower_url_index + 4]  # Add 4 for '.com'
        url_network_part = current_url[lower_url_index + 4:upper_url_index + 7]  # Add 7 for '/manage'
        # For this URL, it doesn't matter which network in an org we get it from because it will be the same
        administered_orgs = url_domain_part + url_network_part + '/organization/administered_orgs'
        self.browser.open(administered_orgs)
        if DEBUG:
            print(administered_orgs)

        cj = self.browser.get_cookiejar()
        if DEBUG:
            print(cj)
        response = requests.get(administered_orgs, cookies=cj)
        administered_orgs_text = response.text

        orgs_dict = json.loads(administered_orgs_text)
        if DEBUG:
            print(orgs_dict)
            print(self.current_org)

        # For network_only_admins, we first get org info from the administered_orgs page
        if self.network_admin_only:
            self.org_qty = len(orgs_dict.keys())
            for i in range(self.org_qty):
                org_id = list(orgs_dict)[i]
                self.org_list.append(orgs_dict[org_id]['name'])
            # Duplicating this line here as we're ok with network admins running this code multiple times as it's
            # dependent on administerd_orgs json. For org admins, we keep it in scrape_orgs() so it runs once
            self.network_list = self.base_url_list = [[]] * self.org_qty
        if DEBUG:
            print("org_qty " + str(self.org_qty))
        for i in range(self.org_qty):  # For every organization
            this_org = list(orgs_dict)[i]  # get this org's id
            num_networks = orgs_dict[this_org]['num_networks']  # int of num networks
            # Inner dict that contains base64 network name and all network info
            node_groups = orgs_dict[this_org]['node_groups']
            # List of network ids in base64. These network ids are keys for network data dict that is the value
            network_base64_ids = list(node_groups.keys())
            # Start out with no network names or network base urls for each organization
            network_names = []
            network_base_urls = []
            # For orgs that are not the current org, we will get the number of networks, but get node_groups of {}
            if node_groups == {}:
                num_networks = 0
            for j in range(num_networks):
                node_group_data = node_groups[network_base64_ids[j]]
                if node_group_data['network_type'] == 'wired' and not node_group_data['is_config_template']:
                    network_names.append(node_group_data['n'])
                    # Reconstructing the base url. 't' is for network name as it appears in URL
                    network_base_urls.append(url_domain_part + '/' + node_group_data['t'] +
                                             '/n/' + node_group_data['eid'] + '/manage')

            # If that network list is empty, then fill it with the network names
            if DEBUG:
                print("self.current_org_index " + str(self.current_org_index))
                print(self.network_list)
            if self.network_list[self.current_org_index] == []:
                if DEBUG:
                    print("Adding networks to list")
                self.network_list[self.current_org_index] = network_names
                self.base_url_list[self.current_org_index] = network_base_urls

            if DEBUG:
                print(self.network_list[i])

        self.refresh_network_dropdown()

    def change_organization(self):
        self.network_dropdown.setEnabled(True)
        self.status.showMessage("Status: Fetching organizations...")
        # Change primary organization
        self.current_org = self.org_dropdown.currentText()
        # If the organization index of network_list is empty (i.e. this network list for this org has never been
        # updated), then get the networks for this organization
        # This makes it so we don't need to get the network list twice for the same organization
        self.current_org_index = self.org_list.index(self.current_org)
        print("In change_organization and this is network list " + str(self.network_list))
        if self.network_list[self.current_org_index] == []:
            print("getting networks from change_organization")
            print("we are getting new info for " + self.current_org + " at index" + str(self.current_org_index))
            self.get_networks()
        else:
            print("we already have that info for " + self.current_org + " at index" + str(self.current_org_index))
            # If we already have the network list, remove the current entries in the network combobox
            # And add the ones corresponding to the selected organization
            self.refresh_network_dropdown()

        self.status.showMessage("Status: Select network")

    def refresh_network_dropdown(self):
        # Remove previous contents of Networks QComboBox and add new ones according to chosen organization
        self.network_dropdown.clear()
        self.network_dropdown.addItems(["-- Select a Network --"])
        self.network_dropdown.addItems(self.network_list[self.current_org_index])

    def scrape_vars(self):
        """
        This method will scrape two things
            + Primary WAN IP address
            + Pre-shared key
        This method will check these things
            + Is client VPN enabled in dashboard?
            - Is this a security appliance that is online?
        """
        if DEBUG:
            print("network dropdown index: " + str(self.network_dropdown.currentIndex()-1))
        current_network_index = self.network_dropdown.currentIndex()-1  # Because dropdown has first option 'select'
        self.current_network = str(self.network_list[self.current_org_index][current_network_index])
        self.status.showMessage("Status: Fetching network data for " + self.current_network + "...")

        client_vpn_url = self.base_url_list[self.current_org_index][current_network_index] \
            + '/configure/client_vpn_settings'
        print("Client VPN url " + client_vpn_url)

        self.client_vpn_text = self.browser.get(client_vpn_url).text
        client_vpn_soup = bs4.BeautifulSoup(self.client_vpn_text, 'lxml')

        self.psk = client_vpn_soup.find("input", {"id": "wired_config_client_vpn_secret", "value": True})['value']
        # Found in html as    ,"client_vpn_enabled":true
        client_vpn_value_index = self.client_vpn_text.find(",\"client_vpn_enabled\"")

        print(self.client_vpn_text[client_vpn_value_index:client_vpn_value_index+27])

        self.scrape_ddns_and_ip()
        # validate_date() MUST come after scrape_ddns_and_ip() because it needs DDNS/IP address
        self.validate_data()

    def scrape_ddns_and_ip(self):
        """ ASSERTS
        * This method gets ddns and ip values for the current network
        * This method should ONLY be called if the user has hit the connect button

        Features
        - Get DDNS name (if enabled)
        - Get primary interface's IP address
        - Verify that virtual_ip == {"public_ip":
        :return:
        """
        fw_status_url = self.base_url_list[self.current_org_index][self.network_dropdown.currentIndex()-1] \
                        + '/nodes/new_wired_status'
        self.fw_status_text = self.browser.get(fw_status_url).text

        # ddns value can be found by searching for '"dynamic_dns_name"'
        ddns_value_start = self.fw_status_text.find("dynamic_dns_name")+19
        ddns_value_end = self.fw_status_text[ddns_value_start:].find('\"') + ddns_value_start
        self.current_ddns=self.fw_status_text[ddns_value_start: ddns_value_end]

        # Primary will always come first, so using find should find it's IP address, even if there's a warm spare
        # Using unique '{"public_ip":' to find primary IP address
        ip_start = self.fw_status_text.find("{\"public_ip\":")+14
        ip_end = self.fw_status_text[ip_start:].find('\"') + ip_start
        self.current_primary_ip=self.fw_status_text[ip_start: ip_end]

    def validate_data(self):
        """
        This method will check all of these values and show which are invalid
        User should not be able to connect if there are any tests that fail (i.e grayed out button)
        Each test should be clickable so that the user can find out more information
        """

        self.status.showMessage("Status: Verifying configuration for " + self.current_network + "...")
        self.validation_list.clear()
        validation_textlist = [
            "Is the MX online?",
            "Can the client ping the firewall's public IP?",
            "Is the user behind the firewall?",
            "Is Client VPN enabled?",
            "Is the user authorized for Client VPN?",
            "Is authentication type Meraki Auth?",
            "Are UDP ports 500/4500 port forwarded through firewall?"]
        has_passed_validation = [True] * 7  # False for failed, True for passed
        for i in range(len(validation_textlist)):
            item = QListWidgetItem(validation_textlist[i])
            self.validation_list.addItem(item)

        # *** TEST 0 ***
        # Is the MX online?
        try:
            is_online_status_code = int(self.fw_status_text[self.fw_status_text.find("status#")+9])
            if is_online_status_code != 0:  # 0 is online, 2 is unreachable. There are probably other statuses
                has_passed_validation[0] = False  # Default for has_passed_validation is true, so we don't need else
        except:
            # No 'status#' in HTML means there is no firewall in that network
            # TODO This error should reset org/network prompt after an error as there's no way to fix an empty network
            # Maybe redirect to adding devices to network
            print("There is no device in this network!")
            # Failure error dialog and then return

        # *** TEST 1 ***
        # Can the client ping the firewall if ICMP is enabled
        # TODO This test should become one of the troubleshooting tests after connection failure because it takes time
        # Ping 4 times
        if self.platform == 'win32':  # Identifies any form of Windows
            ping_string = "ping" + self.current_ddns  # ping 4 times every 1000ms
        else:  # *nix of some kind
            ping_string = "ping -c 5 -i 0.2 " + self.current_primary_ip  # ping 4 times every 200ms
        ping_response = system(ping_string)
        if ping_response != 0:  # Ping responses other than 0 mean failure. Error codes are OS-dependent
            has_passed_validation[1] = False
            # Failure error dialog and then return
            print("Cannot connect to device!")

        # *** TEST 2 ***
        # Is the user behind the firewall?
        print(self.fw_status_text)
        try:
            # This IP is the source public IP that the user is connecting with
            ip_start = self.fw_status_text.find("\"request_ip\":")+14  # Start of IP position
            ip_end = self.fw_status_text[ip_start:].find('\"') + ip_start  # Get the position of the IP end quote
            src_public_ip = self.fw_status_text[ip_start:ip_end]
            if src_public_ip == self.current_primary_ip:  # If public IP address of client == MX IP
                has_passed_validation[2] = False  # Then the user is behind their firewall and client vpn won't work
        except:
            print("Exception during source public IP == MX IP test")
            # TODO Raise exception of some type

        # *** TEST 3 ***
        # Is Client VPN enabled?
        if self.client_vpn_text[self.client_vpn_text.find(",\"client_vpn_enabled\"") + 22] != 't':
            has_passed_validation[3] = False

        for i in range(len(validation_textlist)):
            print("has passed" + str(i) + str(has_passed_validation[i]))
            if has_passed_validation[i]:
                self.validation_list.item(i).setIcon(QIcon(self.cwd + '/media/checkmark-16.png'))
            else:
                self.validation_list.item(i).setIcon(QIcon(self.cwd + '/media/x-mark-16.png'))

        # All the error messages! Once we know what the error dialog landscape looks like down here,
        # we might want to turn this into an error method with params
        if not has_passed_validation[3]:
            self.validation_list.item(3).setIcon(QIcon(self.cwd + '/media/x-mark-16.png'))
            # Error message popup that will take control and that the user will need to acknowledge
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Question)
            error_message.setWindowTitle("Error!")
            error_message.setText('Client VPN is not enabled in Dashboard for this network.'
                                  '\nWould you like this program to enable it for you?')
            error_message.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            error_message.setDefaultButton(QMessageBox.Yes)
            ret = error_message.exec_()
            if ret == QMessageBox.Yes:
                self.enable_client_vpn()

        # *** TEST 4 ***
        # Is user authorized for Client VPN?
            # Program can enable

        # *** TEST 5 ***
        # Authentication type is Meraki Auth?
            # User fixes (for now)

        # *** TEST 6 ***
        # Are either UDP ports 500/4500 being port forwarded through the MX firewall?
            # Program can fix


        self.status.showMessage("Status: Ready to connect to " + self.current_network + ".")

    def enable_client_vpn(self):
        self.feature_in_development()
        pass


    def feature_in_development(self):
        dev_message = QMessageBox()
        dev_message.setIcon(QMessageBox.Information)
        dev_message.setWindowTitle("Meraki Client VPN: Features in Progress")
        dev_message.setText('This feature is currently in progress.')
        dev_message.exec_()

    def main_init_ui(self):
        # Set the Window and Tray Icons
        self.setWindowIcon(QIcon(self.cwd + '/media/miles_meraki.png'))
        tray_icon = QSystemTrayIcon(QIcon(self.cwd + '/media/miles_meraki.png'))
        tray_icon.show()

        # Create a horizontal line above the status bar to highlight it
        self.hline = QFrame()
        self.hline.setFrameShape(QFrame.HLine)
        self.hline.setFrameShadow(QFrame.Sunken)

        self.status = QStatusBar()
        self.status.showMessage("Status: Select organization")
        self.status.setStyleSheet("Background: white")

        self.setWindowTitle('Meraki Client VPN: Main')
        self.org_dropdown = QComboBox()
        self.org_dropdown.addItems(["-- Select an Organzation --"])
        self.network_dropdown = QComboBox()
        self.network_dropdown.setEnabled(False)
        if self.org_qty > 0:
            # Autochoose first organization
            self.current_org = self.org_list[0]
            self.browser.open(list(self.org_links.values())[0])
            if DEBUG:
                print("org_qty > 0")
        else:
            self.current_org = 'Org Placeholder'  # Org name placeholder
            self.network_admin_only = True
            if DEBUG:
                print("org_qty <= 0")

        self.connect_btn = QPushButton("Connect")

        vert_layout = QVBoxLayout()
        vert_layout.addWidget(self.org_dropdown)
        vert_layout.addWidget(self.network_dropdown)
        vert_layout.addStretch()
        vert_layout.addWidget(self.validation_list)
        vert_layout.addWidget(self.connect_btn)
        vert_layout.addWidget(self.hline)
        vert_layout.addWidget(self.status)
        self.cw.setLayout(vert_layout)

        # Get the data we need and remove the cruft we don't
        self.get_networks()
        self.network_dropdown.clear()
        # For network admins, we get org information from administered_orgs json blob
        self.org_dropdown.addItems(self.org_list)

        # When we have the organization, we can scrape networks
        # When the user changes the organization dropdown, call the scrap networks method
        # Only change organization when there are more than 1 organization to change
        self.org_dropdown.currentIndexChanged.connect(self.change_organization)
        self.network_dropdown.activated.connect(self.scrape_vars)

        self.connect_btn.clicked.connect(self.attempt_connection)

    def menu_bars(self):
        bar = self.menuBar()
        # Menu bars
        file_menu = bar.addMenu('&File')
        edit_menu = bar.addMenu('&Edit')
        view_menu = bar.addMenu('&View')
        tshoot_menu = bar.addMenu('&Troubleshoot')
        help_menu = bar.addMenu('&Help')

        # File options
        file_open = QAction('&Open', self)
        file_open.setShortcut('Ctrl+O')
        file_save = QAction('&Save', self)
        file_save.setShortcut('Ctrl+S')
        file_quit = QAction('&Quit', self)
        file_quit.setShortcut('Ctrl+Q')

        # Edit options
        edit_preferences = QAction('&Prefrences', self)
        edit_preferences.setShortcut('Ctrl+P')

        # View options
        view_interfaces = QAction('&Interfaces', self)
        view_interfaces.setShortcut('Ctrl+I')
        view_routing = QAction('&Routing', self)
        view_routing.setShortcut('Ctrl+R')
        view_connection_data = QAction('Connection &Data', self)
        view_connection_data.setShortcut('Ctrl+D')

        # Tshoot options
        tshoot_errors = QAction('Tshoot &Errors', self)
        tshoot_errors.setShortcut('Ctrl+E')
        tshoot_pcap = QAction('Tshoot &with Pcaps', self)
        tshoot_pcap.setShortcut('Ctrl+W')

        # Help options
        help_support = QAction('Get S&upport', self)
        help_support.setShortcut('Ctrl+U')
        help_about = QAction('A&bout', self)
        help_about.setShortcut('Ctrl+B')

        file_menu.addAction(file_open)
        file_menu.addAction(file_save)
        file_menu.addAction(file_quit)
        edit_menu.addAction(edit_preferences)
        view_menu.addAction(view_interfaces)
        view_menu.addAction(view_routing)
        view_menu.addAction(view_connection_data)
        tshoot_menu.addAction(tshoot_errors)
        tshoot_menu.addAction(tshoot_pcap)
        help_menu.addAction(help_support)
        help_menu.addAction(help_about)

        file_open.triggered.connect(self.file_open_action)
        file_save.triggered.connect(self.file_save_action)
        file_quit.triggered.connect(self.file_quit_action)
        edit_preferences.triggered.connect(self.edit_prefs_action)
        view_interfaces.triggered.connect(self.view_interfaces_action)
        view_routing.triggered.connect(self.view_routing_action)
        view_connection_data.triggered.connect(self.view_data_action)
        tshoot_errors.triggered.connect(self.tshoot_error_action)
        tshoot_pcap.triggered.connect(self.tshoot_pcap_action)
        help_support.triggered.connect(self.help_support_action)
        help_about.triggered.connect(self.help_about_action)

    def file_open_action(self):
        # Might use this to open a saved vpn config
        self.feature_in_development()
        pass

    def file_save_action(self):
        # Might use this to save a vpn config
        self.feature_in_development()
        pass

    def file_quit_action(self):
        # Quit
        self.close()

    def edit_prefs_action(self):
        # Preferences should go here. How many settings are here will depend on the feature set
        self.prefs = QDialog()
        layout = QVBoxLayout()
        self.prefs_heading = QLabel('<h1>Preferences</h1>')
        self.split_tunnel = QCheckBox("Split-Tunnel?")
        self.split_tunnel.stateChanged.connect(self.split_tunnel.nextCheckState())
        layout.addWidget(self.prefs_heading)
        layout.addWidget(self.split_tunnel)
        self.prefs.setLayout(layout)
        self.prefs.show()

    def view_interfaces_action(self):
        # If linux/macos > ifconfig
        # If Windows > ipconfig /all
        self.feature_in_development()
        pass

    def view_routing_action(self):
        # If linux/macos > netstat -rn
        # If Windows > route print
        self.feature_in_development()
        pass

    def view_data_action(self):
        self.feature_in_development()
        pass

    def tshoot_error_action(self):
        # In Windows, use powershell: get-eventlog
        self.feature_in_development()
        pass

    def tshoot_pcap_action(self):
        self.feature_in_development()
        pass

    def help_support_action(self):
        # Redirect to Meraki's support website
        webbrowser.open('https://meraki.cisco.com/support')

    def help_about_action(self):
        about_popup = QDialog()
        about_popup.setWindowTitle("Meraki Client VPN: About")
        about_program = QLabel()
        about_program.setText("<h1>Meraki VPN Client 0.5.1</h1>\nDeveloped by Ross Jacobs<br><br><br>"
                              "This project is licensed with the Apache License, which can be viewed below:")
        license_text = open("LICENSE", 'r').read()
        licenses = QTextEdit()
        licenses.setText(license_text)
        licenses.setReadOnly(True)  # People shouldn't be able to edit licenses!
        popup_layout = QVBoxLayout()
        popup_layout.addWidget(about_program)
        popup_layout.addWidget(licenses)
        about_popup.setLayout(popup_layout)
        about_popup.setMinimumSize(600, 200)
        about_popup.exec_()

    def attempt_connection(self):
        if 'Select' not in self.org_dropdown.currentText() and 'Select' not in self.network_dropdown.currentText():
            # Change status to reflect we're connecting. For fast connections, you might not see this message
            self.status.showMessage('Status: Connecting...')

            # Making vpn_name have no spcaes because I haven't figured out how to pass a string with spaces to PS
            network_name = self.network_dropdown.currentText()
            vpn_name = network_name.replace(' ', '_') + '_VPN'
            if self.platform == 'win32':
                arch = platform.architecture()
                if arch == '64bit':
                    powershell_path = 'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe'
                else:  # arch MUST be 32bit if not 64bit
                    powershell_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

                # Sanitize variables for powershell input: '$' -> '`$'
                vpn_name = vpn_name.replace('$', '`$')
                self.psk = self.psk.replace('$', '`$')
                self.username = self.username.replace('$', '`$')
                self.password = self.password.replace('$', '`$')
                self.split_tunnel = '$False'
                # Setting execution policy to unrestricted is necessary so that we can access VPN functions
                # Sending DDNS and IP so if DDNS fails, windows can try IP as well
                result = subprocess.Popen(
                    [powershell_path, '-ExecutionPolicy', 'Unrestricted',
                     self.cwd + '\scripts\connect_windows.ps1', vpn_name, self.psk, self.current_ddns,
                     self.current_primary_ip, self.username, self.password, self.split_tunnel]
                )
                if result:
                    self.status.showMessage('Status: Connected')
                else:
                    self.status.showMessage('Status: Connection Failed')

            elif self.platform == 'darwin':
                args = [self.current_primary_ip, self.username, self.password]
                result = subprocess.Popen(['osascript', '-'] + args, stdout=subprocess.PIPE)

            elif self.platform.startswith('linux'):  # linux, linux2 are both valid
                # bash integration has been verified as working, vpn setup is still work in progress
                result = subprocess.Popen(["./src/scripts/connect_linux.sh", self.current_primary_ip, self.username, self.password])

        else:  # They haven't selected an item in one of the message boxes
            self.error_message('You must select BOTH an organization AND network before connecting!')

        if DEBUG:
            print("Attempting connection...")
        # We're setting up threads to read result's streams to force program to wait
        throwaway_stream = result.communicate()[0]
        print("The return code is " + str(result.returncode))

        if result:
            self.troubleshoot_connection()

    def troubleshoot_connection(self):
        """ Things to check:
        * Basic
            * Is MX online now?
            * Is the client vpn user authorized?
            *
        """

        self.error_message('VPN Connection Failed!')

    def error_message(self, message):
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Critical)
        error_message.setWindowTitle("Error!")
        error_message.setText(message)
        error_message.exec_()

DEBUG = True
app = None


def main():  # Syntax per PyQt recommendations: http://pyqt.sourceforge.net/Docs/PyQt5/gotchas.html
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    # QDialog has two return values: Accepted and Rejected
    # login_window.exec_() will execute while we keep on getting Rejected
    if login_window.exec_() == QDialog.Accepted:
        main_window = MainWindow(login_window.get_browser(), login_window.username, login_window.password)
        main_window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
