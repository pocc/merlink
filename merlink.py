#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls

# Build this with './venv/bin/python3 setup.py build' from project root

# Utilities
import sys
import webbrowser

# Qt5
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QSystemTrayIcon, QTextEdit, QLineEdit, qApp,
                             QVBoxLayout, QComboBox, QMainWindow, QAction, QDialog, QMessageBox, QSpinBox, QMenu,
                             QStatusBar, QFrame, QListWidget, QListWidgetItem, QCheckBox, QHBoxLayout, QRadioButton)
from PyQt5.QtGui import QIcon, QFont

# Web Scraping
import re
import json
import requests
import bs4
import mechanicalsoup

# OS modules
import subprocess
import platform
from os import getcwd, system
import psutil

# Import the login_window file
from src.modules.pyinstaller_path_helper import resource_path
from src.modules.login_window import LoginWindow
from src.modules.is_online import is_online
from src.modules.modal_dialogs import error_dialog, question_dialog
from src.modules.duplicate_application import is_duplicate_application


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

        # Set the Window and Tray Icons
        self.setWindowIcon(QIcon(resource_path('src/media/miles.ico')))

        # Set initial vars for username/password fields for dasboard/guest user
        self.radio_username_label = QLabel("Email")
        self.radio_username_label.setStyleSheet("color: #606060")  # Gray
        self.radio_username_textfield = QLineEdit()
        self.radio_password_label = QLabel("Password")
        self.radio_password_label.setStyleSheet("color: #606060")  # Gray
        self.radio_password_textfield = QLineEdit()
        self.radio_password_textfield.setEchoMode(QLineEdit.Password)

        # Powershell Variables set to defaults
        self.current_ddns = '-'  # set to default hyphen char as a failsafe
        self.split_tunnel = False  # Expected behavior is to have full-tunnel by default
        self.remember_credential = False
        self.DnsSuffix = '-'  # If it's set to '', then powershell will skip reading that parameter.
        self.IdleDisconnectSeconds = 0  # Powershell default indicating that we shouldn't disconnect after x seconds
        self.UseWinlogonCredential = False
        self.is_connected = False

        # QMainWindow requires that a central widget be set
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        # CURRENT minimum width of Main Window - SUBJECT TO CHANGE as features are added
        # self.cw.setMinimumWidth(400)

        self.browser = browser_session
        self.username = username
        self.password = password
        self.scrape_orgs()
        self.main_init_ui()
        self.menu_bars()

    # This function will get the organizations and then save them as a dict of names and links
    def scrape_orgs(self):
        """ ASSERTS
        Don't set data for network-only admins as they don't have org-access.
        Network-only admin data is added in get_networks().
        """

        if DEBUG:
            print("In fn [scrape_orgs()]")

        # NOTE: Until you choose an organization, Dashboard will not let you visit pages you should have access to
        page = self.browser.get_current_page()
        pagetext = page.text  # Use pagetext variable so we can have a string we can use slices with
        is_one_org_admin_index = pagetext.find("org_str")  # Found in HTML for administrators with access to only 1 org
        if is_one_org_admin_index != -1:  # org_str is ONLY found for one org admins
            self.org_qty = 1
        else: 
            # Get a list of all org links
            org_names = page.findAll('a', href=re.compile('/login/org_choose\?eid=.{6}'))
            # Get the number of orgs
            self.org_qty = len(org_names)

        if self.org_qty == 1:  # org admin with one org
            org_name_start = pagetext.find("Mkiconf.org_name") + 20  # This should be present in EVERY dashboard page
            org_name_end = org_name_start + pagetext[org_name_start:].find('\"')
            one_org_name = pagetext[org_name_start: org_name_end]
            self.org_links[one_org_name] = self.browser.get_url()
            self.org_list.append(one_org_name)
        elif self.org_qty > 1:  # 2+ Orgs admin
            for i in range(self.org_qty):
                org_str = str(org_names[i])
                # 39:-4 = Name, 9:37 = Link
                self.org_links[org_str[39:-4]] = 'https://account.meraki.com' + org_str[9:37]
                self.org_list.append(org_str[39:-4])
                print(org_str[39:-4] + self.org_links[org_str[39:-4]])

        # Create as many network lists in the network list as there are orgs
        self.network_list = [[]] * self.org_qty
        self.base_url_list = [[]] * self.org_qty


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
            print("orgs_dict " + str(orgs_dict))
            print("current org " + str(self.current_org))

        # For network_only_admins, we first get org info from the administered_orgs page
        if self.network_admin_only:
            self.org_qty = len(orgs_dict.keys())
            for i in range(self.org_qty):
                org_id = list(orgs_dict)[i]
                self.org_list.append(orgs_dict[org_id]['name'])
            # Duplicating this line here as we're ok with network admins running this code multiple times as it's
            # dependent on administerd_orgs json. For org admins, we keep it in scrape_orgs() so it runs once
            self.network_list = [[]] * self.org_qty
            self.base_url_list = [[]] * self.org_qty
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
        self.get_client_vpn_text()

        self.psk = self.client_vpn_soup.find("input", {"id": "wired_config_client_vpn_secret", "value": True})['value']
        # Found in html as    ,"client_vpn_enabled":true
        client_vpn_value_index = self.client_vpn_text.find(",\"client_vpn_enabled\"")

        print(self.client_vpn_text[client_vpn_value_index:client_vpn_value_index+27])

        self.scrape_ddns_and_ip()
        # validate_date() MUST come after scrape_ddns_and_ip() because it needs DDNS/IP address
        self.validate_data()

    def get_client_vpn_text(self):
        if DEBUG:
            print("network dropdown index: " + str(self.network_dropdown.currentIndex()-1))
        current_network_index = self.network_dropdown.currentIndex()-1  # Because dropdown has first option 'select'
        self.current_network = str(self.network_list[self.current_org_index][current_network_index])
        self.client_vpn_url = self.base_url_list[self.current_org_index][current_network_index] \
            + '/configure/client_vpn_settings'
        self.status.showMessage("Status: Fetching network data for " + self.current_network + "...")
        print("Client VPN url " + self.client_vpn_url)

        self.client_vpn_text = self.browser.get(self.client_vpn_url).text
        self.client_vpn_soup = bs4.BeautifulSoup(self.client_vpn_text, 'lxml')

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
            "Is authentication type Meraki Auth?",
            "Are UDP ports 500/4500 port forwarded through firewall?"]
            # "Is the user authorized for Client VPN?",
        has_passed_validation = [True] * 6  # False for failed, True for passed
        for i in range(len(validation_textlist)):  # For as many times as there are items in the validation_textlist
            item = QListWidgetItem(validation_textlist[i])  # Initialize a QListWidgetItem out of a string
            self.validation_list.addItem(item)  # Add the item to the QListView

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
            error_dialog("There is no device in this network!")
            # Failure error dialog and then return

        # *** TEST 1 ***
        # Can the client ping the firewall if ICMP is enabled
        # TODO This test should become one of the troubleshooting tests after connection failure because it takes time
        # Ping 4 times
        if self.platform == 'win32':  # Identifies any form of Windows
            ping_string = "ping " + self.current_ddns  # ping 4 times every 1000ms
        else:  # *nix of some kind
            ping_string = "ping -c 5 -i 0.2 " + self.current_primary_ip  # ping 4 times every 200ms
        ping_response = system(ping_string)
        if ping_response != 0:  # Ping responses other than 0 mean failure. Error codes are OS-dependent
            has_passed_validation[1] = False
            # Failure error dialog and then return
            error_dialog("Cannot connect to device!")

        # *** TEST 2 ***
        # Is the user behind the firewall?
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

        # *** TEST 4 ***
        # Authentication type is Meraki Auth?
        # User fixes (for now)
        """ When an auth type is selected, we get one of these in the client VPN HTML depending on user's auth choice:
        Meraki cloud</option></select>
        Active Directory</option></select>
        RADIUS</option></select>
        """
        # String find returns -1 if the string isn't found
        meraki_select_type1 = self.client_vpn_text.find('Meraki cloud</option></select>')
        meraki_select_type2 = self.client_vpn_text.find('<option value="meraki" selected="selected">')
        if meraki_select_type1 == -1 and meraki_select_type2 == -1:
            has_passed_validation[4] = False
            print("ERROR: Please select Meraki cloud authentication")
            # TODO Error dialog goes here

        # *** TEST 5 ***
        """ 
        If the following text exists, they're port forwarding ports 500 or 4500:
        "public_port":"500"
        "public_port":"4500"
        """
        # -1 is returned by string find if a match is not found
        is_forwarding_500 = self.client_vpn_text.find('"public_port":"500"') != -1
        is_forwarding_4500 = self.client_vpn_text.find('"public_port":"4500"') != -1
        if is_forwarding_500:
            # TODO Error dialog goes here
            print("ERROR: You are forwarding port 500!")
            has_passed_validation[5] = False

        if is_forwarding_4500:
            # TODO Error dialog goes here
            print("ERROR: You are forwarding port 4500!")
            has_passed_validation[5] = False

        # *** TEST 6 *** : CURRENTLY ON HOLD
        # Is user authorized for Client VPN?
        # By definition, if you can log in as a user, you have a user in the Client VPN users page

        # This is the only test which requires us to scrape data from a table. Tables in dashboard use javascript,
        # So we need to scrape differently.
        # https://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python
        """ from selenium import webdriver
         from selenium.webdriver.chrome.options import Options
         options = Options()
         options.add_argument('--headless')
         # options.add_argument('--disable-gpu')  # Last I checked this was necessary.
         driver = webdriver.Chrome('/usr/bin/google-chrome', chrome_options=options)
         driver.get(self.client_vpn_url)
         print(driver.find_elements_by_css_selector('td.ft.notranslate.email'))
        """

        # ----------------------------------------------
        # Add checkboxes/x-marks to each validation test
        for i in range(len(validation_textlist)):
            print("has passed" + str(i) + str(has_passed_validation[i]))
            print("current directory" + self.cwd)
            if has_passed_validation[i]:
                self.validation_list.item(i).setIcon(QIcon(resource_path('src/media/checkmark-16.png')))
            else:
                self.validation_list.item(i).setIcon(QIcon(resource_path('src/media/x-mark-16.png')))

            # All the error messages! Once we know what the error dialog landscape looks like down here,
            # we might want to turn this into an error method with params
        if not has_passed_validation[3]:
            self.validation_list.item(3).setIcon(QIcon(resource_path('src/media/x-mark-16.png')))
            # Error message popup that will take control and that the user will need to acknowledge
            force_enable_client_vpn = error_dialog('Client VPN is not enabled in Dashboard for this network.'
                                  '\nWould you like this program to enable it for you?')
            if force_enable_client_vpn == QMessageBox.Yes:
                self.enable_client_vpn()

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
        # Create a horizontal line above the status bar to highlight it


        self.hline = QFrame()
        self.hline.setFrameShape(QFrame.HLine)
        self.hline.setFrameShadow(QFrame.Sunken)

        self.status = QStatusBar()
        self.status.showMessage("Status: Select organization")
        self.status.setStyleSheet("Background: white")

        # Title is an NSIS uninstall reference (see Modern.nsh)
        self.setWindowTitle('Merlink - VPN Client for Meraki firewalls')
        self.org_dropdown = QComboBox()
        self.org_dropdown.addItems(["-- Select an Organzation --"])
        self.network_dropdown = QComboBox()
        self.network_dropdown.setEnabled(False)

        self.user_auth_section = QVBoxLayout()
        self.radio_user_layout = QHBoxLayout()
        self.user_auth_section.addLayout(self.radio_user_layout)
        self.radio_dashboard_admin_user = QRadioButton("Dashboard Admin")
        self.radio_dashboard_admin_user.setChecked(True)  # Default is to have dashboard user
        self.radio_guest_user = QRadioButton("Guest User")
        self.radio_user_layout.addWidget(self.radio_dashboard_admin_user)
        self.radio_user_layout.addWidget(self.radio_guest_user)
        self.set_dashboard_user_layout()  # Default is to use dashboard user
        self.radio_dashboard_admin_user.toggled.connect(self.set_dashboard_user_layout)
        self.radio_guest_user.toggled.connect(self.set_guest_user_layout)

        self.user_auth_section.addWidget(self.radio_username_label)
        self.user_auth_section.addWidget(self.radio_username_textfield)
        self.user_auth_section.addWidget(self.radio_password_label)
        self.user_auth_section.addWidget(self.radio_password_textfield)

        if self.org_qty > 0:
            # Autochoose first organization
            self.current_org = self.org_list[0]
            self.browser.open(list(self.org_links.values())[0])
        else:
            self.current_org = 'Org Placeholder'  # Org name placeholder
            self.network_admin_only = True

        # Ask the user for int/str values if they want to enter them
        self.idle_disconnect_layout = QHBoxLayout()
        self.idle_disconnect_chkbox = QCheckBox("Idle disconnect seconds?")
        self.idle_disconnect_spinbox = QSpinBox()
        self.idle_disconnect_spinbox.setValue(0)
        self.idle_disconnect_spinbox.setMinimum(0)  # Negative seconds aren't useful here
        self.idle_disconnect_layout.addWidget(self.idle_disconnect_chkbox)
        self.idle_disconnect_layout.addWidget(self.idle_disconnect_spinbox)

        self.dns_suffix_layout = QHBoxLayout()
        self.dns_suffix_chkbox = QCheckBox("DNS Suffix?")  # Add a textbox here
        self.dns_suffix_txtbox = QLineEdit('-')
        self.dns_suffix_layout.addWidget(self.dns_suffix_chkbox)
        self.dns_suffix_layout.addWidget(self.dns_suffix_txtbox)

        # Boolean asks of the user
        self.split_tunneled_chkbox = QCheckBox("Split-Tunnel?")
        self.remember_credential_chkbox = QCheckBox("Remember Credentials?")
        self.use_winlogon_chkbox = QCheckBox("Use Windows Logon Credentials")

        self.connect_btn = QPushButton("Connect")

        vert_layout = QVBoxLayout()

        # Add Dashboard Entry-only dropdowns
        vert_layout.addWidget(self.org_dropdown)
        vert_layout.addWidget(self.network_dropdown)
        vert_layout.addLayout(self.user_auth_section)
        vert_layout.addWidget(self.validation_list)

        # Add layouts for specialized params
        vert_layout.addLayout(self.idle_disconnect_layout)
        vert_layout.addLayout(self.dns_suffix_layout)

        # Add checkboxes
        vert_layout.addWidget(self.split_tunneled_chkbox)
        vert_layout.addWidget(self.remember_credential_chkbox)
        vert_layout.addWidget(self.use_winlogon_chkbox)

        # Add stuff at bottom
        vert_layout.addWidget(self.connect_btn)
        vert_layout.addWidget(self.hline)
        vert_layout.addWidget(self.status)
        self.cw.setLayout(vert_layout)

        # Get the data we need and remove the cruft we don't
        self.get_networks()
        self.network_dropdown.clear()
        # For network admins, we get org information from administered_orgs json blob
        for i in range(len(self.org_list)):
            print(self.org_list[i])
        self.org_dropdown.addItems(self.org_list)

        # When we have the organization, we can scrape networks
        # When the user changes the organization dropdown, call the scrap networks method
        # Only change organization when there are more than 1 organization to change

        self.systray_icon()

        self.org_dropdown.currentIndexChanged.connect(self.change_organization)
        self.network_dropdown.activated.connect(self.scrape_vars)

        self.connect_btn.clicked.connect(self.attempt_connection)

    def close_window(self):
        self.close()

    def systray_icon(self):
        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path('src/media/miles.ico')))
        if self.is_vpn_connected():
            connection_status = 'VPN connected'
        else:
            connection_status = 'VPN disconnected'
        self.tray_icon.setToolTip("Merlink - " + connection_status)

        # TODO this should be a drop down of saved connections
        connect_action = QAction("Connect to ...", self)
        # These 3 lines are to make "Connect to ..." bold
        f = QFont()
        f.setBold(True)
        connect_action.setFont(f)

        disconnect_action = QAction("Disconnect", self)
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        connect_action.triggered.connect(self.attempt_connection)  # Allow this if we're not connected
        disconnect_action.triggered.connect(self.disconnect)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)

        tray_menu = QMenu()
        tray_menu.addAction(connect_action)
        tray_menu.addAction(disconnect_action)
        tray_menu.addSeparator()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # If they click on the connected message, show them the VPN connection
        self.tray_icon.activated.connect(self.icon_activated)  # If systray icon is clicked

    def open_vpn_settings(self):
        # Opens Windows 10 Settings > Network & Internet > VPN
        system('start ms-settings:network-vpn')

    def icon_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show()  # So it will show up in taskbar
            self.raise_()  # for macOS
            self.activateWindow()  # for Windows

        elif reason == QSystemTrayIcon.MiddleClick:
            # Go to Security Appliance that we've connected to
            # TODO This is going to need more legwork as we need to pass the cookie when we open the browser
            webbrowser.open("https://meraki.cisco.com/")

        # Override closeEvent, to intercept the window closing event
        # The window will be closed only if there is no check mark in the check box

    def closeEvent(self, event):
        event.ignore()
        self.tray_icon.showMessage(  # Show the user the message so they know where the program went
            "Merlink",
            "Merlink is now minimized",
            QSystemTrayIcon.Information,
            1000
        )
        self.hide()

    def set_dashboard_user_layout(self):
        self.radio_username_textfield.setText(self.username)
        self.radio_username_textfield.setReadOnly(True)
        self.radio_password_textfield.setText(self.password)
        self.radio_password_textfield.setReadOnly(True)

    def set_guest_user_layout(self):
        self.radio_username_textfield.clear()
        self.radio_username_textfield.setReadOnly(False)
        self.radio_password_textfield.clear()
        self.radio_password_textfield.setReadOnly(False)

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
        layout.addWidget(self.prefs_heading)
        self.prefs.setLayout(layout)
        self.prefs.show()

    def invert_bool(self, boolvar):
        return not boolvar

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
        if DEBUG:
            print("entering attempt_connection function")
        # If they've selected organization and network OR they've entered everything manually
        if ('Select' not in self.org_dropdown.currentText() and 'Select' not in self.network_dropdown.currentText()) \
                or self.data_entry_tabs.currentIndex() == 1:
            # Change status to reflect we're connecting. For fast connections, you might not see this message
            self.status.showMessage('Status: Connecting...')
            result = 1  # If result doesn't get assigned, we assume program to have failed

            # Making vpn_name have no spcaes because I haven't figured out how to pass a string with spaces to PS
            network_name = self.network_dropdown.currentText()
            # Set VPN name to the network name +/- cosmetic things
            vpn_name = network_name.replace('- appliance', '') + '- VPN'

            if self.radio_dashboard_admin_user.isChecked() == 0:  # If the user is logging in as a guest user
                self.username = self.radio_username_textfield.text()
                self.password = self.radio_password_textfield.text()

            if self.platform == 'win32':
                arch = platform.architecture()
                if arch == '64bit':
                    powershell_path = 'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe'
                else:  # arch MUST be 32bit if not 64bit
                    powershell_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

                # Sanitize variables for powershell input: '$' -> '`$'
                vpn_name = vpn_name.replace('$', '`$')
                self.psk = self.psk.replace('$', '`$')
                self.param_username = self.username.replace('$', '`$')
                self.param_password = self.password.replace('$', '`$')

                # Get values from spinboxes/textfields
                self.IdleDisconnectSeconds = self.idle_disconnect_spinbox.value()
                self.DnsSuffix = self.dns_suffix_txtbox.text()
                if self.DnsSuffix.isspace():  # If they've only submitted space, convert to '-' so PS will not break
                    self.DnsSuffix = '-'

                # Get values from checkboxes and text fields
                self.split_tunnel = self.split_tunneled_chkbox.checkState()
                self.remember_credential = self.remember_credential_chkbox.checkState()
                self.UseWinlogonCredential = self.use_winlogon_chkbox.checkState()

                if DEBUG:
                    print("attempting to connect via powershell script")

                # Arguments sent to powershell MUST BE STRINGS
                # Each argument cannot be the empty string or null or PS will think there's no param there!!!
                # Last 3 ps params are bools converted to ints (0/1) converted to strings. It's easy to force convert
                # '0' and '1' to ints on powershell side
                # Setting execution policy to unrestricted is necessary so that we can access VPN functions
                # TODO Verify that resource_path and the connect script works on Windows
                result = subprocess.call(
                        [powershell_path, '-ExecutionPolicy', 'Unrestricted',
                         resource_path('\src\scripts\connect_windows.ps1'), vpn_name, self.psk, self.current_ddns,
                         self.current_primary_ip, self.param_username, self.param_password, self.DnsSuffix,
                         str(self.IdleDisconnectSeconds),  str(DEBUG), str(int(self.split_tunnel)),
                         str(int(self.remember_credential)), str(int(self.UseWinlogonCredential))])
                # subprocess.Popen([], creationflags=subprocess.CREATE_NEW_CONSOLE)  # open ps window
                print("MainWindow and the result is " + str(result) + str(type(result)))
                if result == 0:
                    self.is_connected = True
                    self.status.showMessage('Status: Connected')
                    success_message = QMessageBox()
                    success_message.setIcon(QMessageBox.Information)
                    success_message.setWindowTitle("Success!")
                    success_message.setText("Successfully Connected!")
                    success_message.exec_()

                    # There's no such thing as "minimize to system tray". What we're doing is hiding the window and
                    # then adding an icon to the system tray

                    # Show this when connected
                    self.tray_icon.setIcon(QIcon(resource_path('src/media/connected_miles.ico')))
                    # If user wants to know more about connection, they can click on message and be redirected
                    self.tray_icon.messageClicked.connect(self.open_vpn_settings)
                    self.tray_icon.showMessage(  # Show the user the message so they know where the program went
                        "Merlink",
                        "Succesfully connected!",
                        QSystemTrayIcon.Information,
                        2000
                    )
                    self.hide()

                else:
                    self.is_connected = False
                    self.status.showMessage('Status: Connection Failed')
                    self.error_dialog("Connection Failed")
                    self.tray_icon.setIcon(QIcon(resource_path('src/media/unmiles.ico')))

            elif self.platform == 'darwin':
                print("Creating macOS VPN")
                # scutil is required to add the VPN to the active set. Without this, it is
                #   not possible to connect, even if a VPN is listed in Network Services
                # scutil --nc select <connection> throws '0:227: execution error: No service (1)'
                #   if it's a part of the build script instead of here.
                # This is why it's added directly to the osacript request.
                # Connection name with forced quotes in case it has spaces.

                scutil_string = 'scutil --nc select ' + '\'' + vpn_name + '\''
                print("scutil_string: " + scutil_string)
                # Create an applescript execution string so we don't need to bother with parsing arguments with Popen
                command = 'do shell script \"/bin/bash src/scripts/build_macos_vpn.sh' + ' \'' + vpn_name + '\' \'' \
                    + self.current_ddns + '\' \'' + self.psk + '\' \'' + self.username + '\' \'' + self.password \
                    + '\'; ' + scutil_string + '\" with administrator privileges'
                # Applescript will prompt the user for credentials in order to create the VPN connection
                print("command being run: " + command)
                result = subprocess.Popen(['/usr/bin/osascript', '-e', command], stdout=subprocess.PIPE)

                # Get the result of VPN creation and print
                output = result.stdout.read()
                print(output.decode('utf-8'))

                # Connect to VPN.
                # Putting 'f' before a string allows you to insert vars in scope
                print("Connecting to macOS VPN")
                print("Current working directory: " + str(system('pwd')))
                subprocess.call(['bash', 'src/scripts/connect_macos.sh', vpn_name])

            elif self.platform.startswith('linux'):  # linux, linux2 are both valid
                # sudo required to create a connection with nmcli
                # pkexec is built into latest Fedora, Debian, Ubuntu.
                # 'pkexec <cmd>' correctly asks in GUI on Debian, Ubuntu but in terminal on Fedora
                # pkexec is PolicyKit, which is the preferred means of asking for permission on LSB
                system('chmod a+x ' + resource_path('src/scripts/connect_linux.sh'))  # set execution bit on bash script
                result = subprocess.Popen(['pkexec', resource_path('src/scripts/connect_linux.sh'), vpn_name,
                                           self.current_ddns, self.psk, self.username, self.password])

            if result == 1:
                self.troubleshoot_connection()

        else:  # They haven't selected an item in one of the message boxes
            self.error_dialog('You must select BOTH an organization AND network before connecting!')

    def troubleshoot_connection(self):
        print("ACTIVELY troubleshooting connection")
        self.error_dialog('VPN Connection Failed!')

    def disconnect(self):
        if self.is_vpn_connected():
            system('rasdial ' + self.vpn_name + ' /disconnect')
        else:
            self.error_dialog("ERROR: You cannot disconnect if you are not connected!")

    def is_vpn_connected(self):
        if self.platform == 'win32':
            rasdial_status = subprocess.Popen(['rasdial'], stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
            return 'Connected to' in rasdial_status


DEBUG = True


def main():  # Syntax per PyQt recommendations: http://pyqt.sourceforge.net/Docs/PyQt5/gotchas.html
    app = QApplication(sys.argv)
    if is_duplicate_application():
        error_dialog('ERROR: You already have a running instance of merlink!'
                     '\nThis application will now close.')
        sys.exit(app.exec_())

    app.setQuitOnLastWindowClosed(False)  # We want to be able to be connected with VPN with systray icon
    login_window = LoginWindow()
    # QDialog has two return values: Accepted and Rejected
    # login_window.exec_() will execute while we keep on getting Rejected
    if login_window.exec_() == QDialog.Accepted:
        main_window = MainWindow(login_window.get_browser(), login_window.username, login_window.password)
        main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
