#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls

# System
import sys

# Qt5
from PyQt5.QtWidgets import (QApplication, QLineEdit, QWidget, QPushButton, QLabel, QSystemTrayIcon,
                             QVBoxLayout, QHBoxLayout, QComboBox, QMainWindow, QAction, QDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QIcon

# Web Scraping
import mechanicalsoup
import re
import json
import requests
import bs4

# VPN creation
import subprocess
import platform
import os

class LoginWindow(QDialog):
    def __init__(self):
        if DEBUG:
            print("In Login Window")

        super(LoginWindow, self).__init__()

        self.meraki_img = QLabel()

        # Copying style from Dashboard Login (https://account.meraki.com/login/dashboard_login)
        self.heading_style = "font-family: verdana, sans-serif; font-style: normal; " \
                             "font-size: 28px; font-weight: 300; color:  #666;"
        self.label_style = "font-family: verdana, sans-serif; font-style: normal; " \
                           "font-size: 13px; color: #000;"
        # Get back to login button style when you can change the color when it's clicked
        # self.login_btn_style = "border-radius: 2px; color: #fff; background: #7ac043"
        self.link_style = "font-family: verdana, sans-serif; font-style: normal; font-size: 13px; color: #1795E6;"

        self.heading = QLabel("Dashboard Login")
        self.heading.setStyleSheet(self.heading_style)
        self.username_lbl = QLabel("Email")
        self.username_lbl.setStyleSheet(self.label_style)
        self.password_lbl = QLabel("Password")
        self.password_lbl.setStyleSheet(self.label_style)
        self.username_field = QLineEdit(self)
        self.password_field = QLineEdit(self)
        # Set up username and password so these vars have values
        self.username = ''
        self.password = ''

        # Masks password as a series of dots instead of characters
        self.password_field.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Log in")

        # self.login_btn.setStyleSheet(self.login_btn_style)
        self.forgot_password_lbl = QLabel("<a href=\"https://account.meraki.com/login/reset_password\" "
                                          "style=\"color:#1795E6;text-decoration:none\">I forgot my password</a>")
        self.forgot_password_lbl.setStyleSheet(self.link_style)
        self.forgot_password_lbl.setOpenExternalLinks(True)
        self.create_account_lbl = QLabel("<a href=\"https://account.meraki.com/login/signup\" "
                                         "style=\"color:#1795E6;text-decoration:none\">Create an account</a>")
        self.create_account_lbl.setStyleSheet(self.link_style)
        self.create_account_lbl.setOpenExternalLinks(True)
        self.about_lbl = QLabel("<a href=\"https://github.com/pocc/meraki-client-vpn\" "
                                "style=\"color:#1795E6;text-decoration:none\">About</a>")
        self.about_lbl.setStyleSheet(self.link_style)
        self.about_lbl.setOpenExternalLinks(True)

        self.init_ui()

    def init_ui(self):
        layout_login_options = QHBoxLayout()
        layout_login_options.addWidget(self.forgot_password_lbl)
        layout_login_options.addStretch()
        layout_login_options.addWidget(self.create_account_lbl)

        # Create a widget to contain the login layout. This allows us to paint the background of the widget
        login_widget = QWidget(self)
        login_widget.setStyleSheet("background-color:white")
        # Create labels and textboxes to form a login layout
        layout_login = QVBoxLayout(login_widget)
        layout_login.addWidget(self.heading)
        layout_login.addWidget(self.username_lbl)
        layout_login.addWidget(self.username_field)
        layout_login.addWidget(self.password_lbl)
        layout_login.addWidget(self.password_field)
        layout_login.addWidget(self.login_btn)
        # Should prevent users from decreasing the size of the window past the minimum
        # Add a stretch so that all elements are at the top, regardless of user resizes
        layout_login.addLayout(layout_login_options)
        layout_login.addStretch()
        layout_login.addWidget(self.about_lbl)

        self.meraki_img.setPixmap(QPixmap('meraki_connections.png'))
        # Background for program will be #Meraki green = #78be20
        self.setStyleSheet("background-color:#eee")
        layout_main = QHBoxLayout()
        layout_main.addWidget(self.meraki_img)
        layout_main.addWidget(login_widget)
        self.setLayout(layout_main)
        self.setWindowTitle('Meraki Client VPN')

        # Test connection with a virtual browser
        self.login_btn.clicked.connect(self.init_browser)

    def init_browser(self):
        self.username = self.username_field.text()
        self.password = self.password_field.text()
        # Instantiate browser
        self.browser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},  # Use the lxml HTML parser
            raise_on_404=True,
            user_agent='MyBot/0.1: mysite.example.com/bot_info',
        )

        # Navigate to login page
        self.browser.open('https://account.meraki.com/login/dashboard_login')
        form = self.browser.select_form()
        self.browser["email"] = self.username
        self.browser["password"] = self.password
        form.choose_submit('commit')  # Click login button
        resp = self.browser.submit_selected()  # resp should be '<Response [200]>'
        self.result_url = self.browser.get_url()

        # After setting everything up, let's see whether user authenticates correctly
        self.attempt_login()

    def attempt_login(self):
        # URL contains /login/login if login failed
        if '/login/login' not in self.result_url:
            self.accept()
        else:
            # Error message popup that will take control and that the user will need to acknowledge
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setWindowTitle("Error!")
            error_message.setText('ERROR: Invalid username or password.')
            error_message.exec_()

            # Sanitize password field so they can reenter credentials
            ''' Design choice: Don't reset username as reentering can be annyoying if only password is wrong
                self.username_field.setText('')'''
            self.password_field.setText('')

            # Return 'Rejected' as value from QDialog object
            self.reject()

    # Return browser with any username, password, and cookies with it
    def get_browser(self):
        return self.browser


class MainWindow(QMainWindow):
    # Pass in browser_session object from LoginWindow so that we can maintain the same session
    def __init__(self, browser_session, username, password):
        super(MainWindow, self).__init__()
        if DEBUG:
            print("Main Window")

        # Variables
        self.network_admin_only = False
        self.current_org_index = 0  # By default, we choose the first org to display
        self.org_qty = 0  # By default, you have access to 0 orgs
        # Initialize organization dictionary {Name: Link} and list for easier access. org_list is org_links.keys()
        self.org_links = {}
        self.org_list = []
        self.base_urls = []

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
        print("init network_list" + str(self.network_list))
        for i in range(self.org_qty):
            org_str = str(org_hrefs[i])
            # 39:-4 = Name, 9:37 = Link
            self.org_links[org_str[39:-4]] = 'https://account.meraki.com' + org_str[9:37]
            self.org_list.append(org_str[39:-4])
            print(org_str[39:-4] + self.org_links[org_str[39:-4]])

    def select_org(self):
        pass

    def get_networks(self):
        """ ASSERTS
        * get_networks should only be called on initial startup or if a different organization has been chosen
        * browser should be initialized
        * browser should have clicked on an org in the org selection page so we can browse relative paths of an org
        """
        if DEBUG:
            print("In get_networks")

        # If we're dealing with org admins
        if not self.network_admin_only:
            # This method will get the networks by using the administered_orgs json blob
            current_url = self.org_links[self.current_org]
            self.browser.open(current_url)
        current_url = self.browser.get_url()
        # base url is up to '/manage/'
        base_url_index = current_url.find('/manage')
        current_base_url = current_url[:base_url_index + 7]  # Add 7 for '/manage'
        self.base_urls.append(current_base_url)
        administered_orgs = current_base_url + '/organization/administered_orgs'
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
            self.network_list = [[]] * self.org_qty
        if DEBUG:
            print("org_qty " + str(self.org_qty))
        for i in range(self.org_qty):  # For every organization
            this_org = list(orgs_dict)[i]  # get this org's id
            num_networks = orgs_dict[this_org]['num_networks']  # int of num networks
            # Inner dict that contains base64 network name and all network info
            node_groups = orgs_dict[this_org]['node_groups']
            # List of network ids in base64. These network ids are keys for network data dict that is the value
            network_base64_ids = list(node_groups.keys())
            # Start out with no network names for each organization
            network_names = []
            # For orgs that are not the current org, we will get the number of networks, but get node_groups of {}
            if node_groups == {}:
                num_networks = 0
            for j in range(num_networks):
                node_group_data = node_groups[network_base64_ids[j]]
                if node_group_data['network_type'] == 'wired' and not node_group_data['is_config_template']:
                    network_names.append(node_group_data['n'])

            # If that network list is empty, then fill it with the network names
            if DEBUG:
                print("self.current_org_index " + str(self.current_org_index))
                print(self.network_list)
            if self.network_list[self.current_org_index] == []:
                if DEBUG:
                    print("Adding network to list")
                self.network_list[self.current_org_index] = network_names
            if DEBUG:
                print(self.network_list[i])

        self.refresh_network_dropdown()

    def change_organization(self):
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

    def refresh_network_dropdown(self):
        # Remove previous contents of Networks QComboBox and add new ones according to chosen organization
        self.network_dropdown.clear()
        self.network_dropdown.addItems(["-- Select a Network --"])
        self.network_dropdown.addItems(self.network_list[self.current_org_index])

    def scrape_psk(self):
        """
        This method will scrape two things
            - Primary WAN IP address
            + Pre-shared key
        This method will check these things
            + Is client VPN enabled in dashboard?
            - Is this a security appliance that is online?
        """

        client_vpn_url = self.base_urls[self.current_org_index] + '/configure/client_vpn_settings'
        print(client_vpn_url)
        client_vpn_text = self.browser.get(client_vpn_url).text
        client_vpn_soup = bs4.BeautifulSoup(client_vpn_text, 'lxml')

        self.psk = client_vpn_soup.find("input", {"id": "wired_config_client_vpn_secret", "value": True})['value']
        # Found in html as    ,"client_vpn_enabled":true
        client_vpn_value_index = client_vpn_text.find(",\"client_vpn_enabled\"")

        print(client_vpn_text[client_vpn_value_index:client_vpn_value_index+27])
        if client_vpn_text[client_vpn_text.find(",\"client_vpn_enabled\"")+22] == 'f':

            # Error message popup that will take control and that the user will need to acknowledge
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Question)
            error_message.setWindowTitle("Error!")
            error_message.setText('Client VPN is not enabled in Dashboard.'
                                  '\nWould you like this program to enable it for you?')
            error_message.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            error_message.setDefaultButton(QMessageBox.Yes)
            ret = error_message.exec_()
            if ret == QMessageBox.Yes:
                self.enable_client_vpn()

    def enable_client_vpn(self):
        self.feature_in_development()
        pass

    def scrape_ddns_and_ip(self):
        """ ASSERTS
        * This method gets ddns and ip values for the current network
        * This method should ONLY be called if the user has hit the connect button

        Features
        - Get DDNS name (if enabled)
        - Get primary interface's IP address
        - Verify that virtual_ip == {"public_ip":
        TODO verify that this method of getting IP address works on all combinations of warm spares and virtual ips
        TODO Find out whether it would be faster to add a json blob object and search that vis-a-vis this solution
        :return:
        """
        fw_status_url = self.base_urls[self.current_org_index] + '/nodes/new_wired_status'
        fw_status_text = self.browser.get(fw_status_url).text

        # ddns value can be found by searching for '"dynamic_dns_name"'
        ddns_value_start = fw_status_text.find("dynamic_dns_name")+19
        ddns_value_end = fw_status_text[ddns_value_start:].find('\"') + ddns_value_start
        self.current_ddns=fw_status_text[ddns_value_start: ddns_value_end]

        # Primary will always come first, so using find should find it's IP address, even if there's a warm spare
        # Using unique '{"public_ip":' to find primary IP address
        ip_start = fw_status_text.find("{\"public_ip\":")+14
        ip_end = fw_status_text[ip_start:].find('\"') + ip_start
        self.current_primary_ip=fw_status_text[ip_start: ip_end]

    def feature_in_development(self):
        dev_message = QMessageBox()
        dev_message.setIcon(QMessageBox.Information)
        dev_message.setWindowTitle("Meraki Client VPN: Features in Progress")
        dev_message.setText('This feature is currently in progress.')
        dev_message.exec_()

    def main_init_ui(self):
        # Set the Window Icon
        self.setWindowIcon(QIcon('miles_meraki.png'))
        # Set the tray icon and show it
        tray_icon = QSystemTrayIcon(QIcon('miles_meraki.png'))
        tray_icon.show()

        self.setWindowTitle('Meraki Client VPN: Main')
        self.org_dropdown = QComboBox()
        self.org_dropdown.addItems(["-- Select an Organzation --"])
        self.network_dropdown = QComboBox()
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
        vert_layout.addWidget(self.connect_btn)
        self.cw.setLayout(vert_layout)

        self.get_networks()
        # For network admins, we get org information from administered_orgs json blob
        self.org_dropdown.addItems(self.org_list)

        """# Gray out comboboxes if there's only one option for org or network
        # Currently disabling this as it's not strictly necessary
        if self.org_qty == 1:
            self.org_dropdown.setEnabled(False)
        if len(self.network_list[self.current_org_index]) == 1:
            self.network_dropdown.setEnabled(False)"""

        # When we have the organization, we can scrape networks
        # When the user changes the organization dropdown, call the scrap networks method
        # Only change organization when there are more than 1 organization to change
        self.org_dropdown.currentIndexChanged.connect(self.change_organization)
        self.network_dropdown.activated.connect(self.scrape_psk)
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
        help_support = QAction('S&upport', self)
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
        self.feature_in_development()
        pass

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
        # Redirect to https://meraki.cisco.com/support
        self.feature_in_development()
        pass

    def help_about_action(self):
        # Talk about yourself
        # Also, pre-alpha, version -1
        # Apache License
        self.feature_in_development()
        pass

    def attempt_connection(self):
        if 'Select' not in self.org_dropdown.currentText() and 'Select' not in self.network_dropdown.currentText():
            self.scrape_ddns_and_ip()
            if sys.platform == 'win32':
                arch = platform.architecture()
                if arch == '64bit':
                    powershell_path = 'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe'
                else:  # arch MUST be 32bit if not 64bit
                    powershell_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

                # Setting execution policy to unrestricted is necessary so that we can access VPN functions
                # Sending DDNS and IP so if DDNS fails, windows can try IP as well
                ps_vpn = subprocess.Popen(
                    [powershell_path, '-ExecutionPolicy', 'Unrestricted', './connect_windows.ps1',
                     self.current_ddns, self.current_primary_ip, self.username, self.password], cwd=os.getcwd()
                )
                result = ps_vpn.wait()
                print(result)

            elif sys.platform == 'darwin':
                self.feature_in_development()
                pass

            elif sys.platform.startswith('linux'):  # linux, linux2 are both valid

                pass

        else:
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setWindowTitle("Error!")
            error_message.setText('You must select an organization and network before connecting!')
            error_message.exec_()
            pass

        # This is where OS-specific code will go
        if DEBUG:
            print("Attempting connection...")
        pass


DEBUG = True
app = None


def main():  # Syntax per PyQt recommendations: http://pyqt.sourceforge.net/Docs/PyQt5/gotchas.html
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    # QDialog has two return values: Accepted and Rejected
    # login_window.exec_() will execute while we keep on getting Rejected
    while login_window.exec_() != QDialog.Accepted:
        pass
    main_window = MainWindow(login_window.get_browser(), login_window.username, login_window.password)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
