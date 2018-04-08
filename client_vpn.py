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
        self.browser = mechanicalsoup.StatefulBrowser()

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

            # Sanitize fields so they can reenter credentials
            self.password_field.setText('')
            self.username_field.setText('')

            # Return 'Rejected' as value from QDialog object
            self.reject()

    # Return browser with any username, password, and cookies with it
    def get_browser(self):
        return self.browser


class MainWindow(QMainWindow):
    # Pass in browser_session object from LoginWindow so that we can maintain the same session
    def __init__(self, browser_session):
        super(MainWindow, self).__init__()
        if DEBUG:
            print("Main Window")

        # QMainWindow requires that a central widget be set
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        # CURRENT minimum width of Main Window - SUBJECT TO CHANGE as features are added
        self.cw.setMinimumWidth(330)

        self.browser = browser_session
        self.scrape_orgs()
        self.current_org = self.org_list[0]
        self.main_init_ui()
        self.menu_bars()
        self.select_network()  # Once an organization has been selected, networks will start populating for that org
        # -------------------------
        # When you have ALL the information
        self.attempt_connection()

    # This function will get the organizations and then save them as a dict of names and links
    def scrape_orgs(self):
        # NOTE: Until you choose an organization, Dashboard will not let you visit pages you should have access to
        page = self.browser.get_current_page()
        # Get a list of all org links
        org_hrefs = page.findAll('a', href=re.compile('/login/org_choose\?eid=.{6}'))
        # Get the number of orgs
        self.org_qty = len(org_hrefs)
        # Initialize organization dictionary {Name: Link} and list for easier access
        self.org_links = {}
        self.org_list = []
        for i in range(self.org_qty):
            org_str = str(org_hrefs[i])
            # 39:-4 = Name, 9:37 = Link
            self.org_links[org_str[39:-4]] = 'https://account.meraki.com' + org_str[9:37]
            self.org_list.append(org_str[39:-4])

    def select_org(self):
        pass

    def get_networks(self):
        # This method will get the networks by using the administered_orgs json blob
        current_url = self.browser.get_url()
        # base_url is up to '/manage/'
        base_url_index = current_url.find('/manage')
        base_url = current_url[:base_url_index + 7]  # Add 7 for '/manage'
        administered_orgs = base_url + '/organization/administered_orgs'
        print(type(administered_orgs))
        print(administered_orgs)
        self.browser.open(administered_orgs)
        print(self.browser.get(administered_orgs))
        breakpoint()


        self.orgs_json = json.loads(str(administered_orgs_text))

        # Network list will be a list of networks ordered by alphabetical organization order
        # This will be the same organizational ordering as org_links
        self.network_list = []

        for i in range(self.org_qty):  # For every organization
            this_org = list(self.orgs_json)[i]  # get this org's id
            num_networks = self.orgs_json[this_org]['num_networks']
            node_group_data = self.orgs_json[list(self.orgs_json)[0]]['node_groups']
            network_names = []
            for j in range(num_networks):
                node_group_id = list(node_group_data)[j]
                network_names.append(node_group_data[node_group_id]['n'])
            self.network_list.append(network_names)
            print(network_names)

    def main_init_ui(self):
        # Set the Window Icon
        self.setWindowIcon(QIcon('miles_meraki.png'))
        # Set the tray icon and show it
        tray_icon = QSystemTrayIcon(QIcon('miles_meraki.png'))
        tray_icon.show()

        self.setWindowTitle('Meraki Client VPN: Main')
        self.Organizations = QComboBox()
        if self.org_qty > 0:
            # Autochoose first organization
            self.browser.open(list(self.org_links.values())[0])
            self.Organizations.addItems(self.org_list)
            if DEBUG:
                print("org_qty > 0")
        else:
            self.get_networks()
            if DEBUG:
                print("org_qty <= 0")

        self.Networks = QComboBox()
        self.connect_btn = QPushButton("Connect")

        vert_layout = QVBoxLayout()
        vert_layout.addWidget(self.Organizations)
        vert_layout.addWidget(self.Networks)
        vert_layout.addStretch()
        vert_layout.addWidget(self.connect_btn)
        self.cw.setLayout(vert_layout)

        # When we have the organization, we can scrape networks
        # When the user changes the organization dropdown, call the scrap networks method
        # Only change organization when there are more than 1 organization to change
        self.Organizations.activated.connect(self.get_networks())

        #self.Networks.addItems(self.network_list[0])

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
        pass

    def file_save_action(self):
        # Might use this to save a vpn config
        pass

    def file_quit_action(self):
        # Quit
        self.close()

    def edit_prefs_action(self):
        # Preferences should go here. How many settings are here will depend on the feature set
        pass

    def view_interfaces_action(self):
        # If linux/macos > ifconfig
        # If Windows > ipconfig /all
        pass

    def view_routing_action(self):
        # If linux/macos > netstat -rn
        # If Windows > route print
        pass

    def view_data_action(self):
        pass

    def tshoot_error_action(self):
        # In Windows, use powershell: get-eventlog
        pass

    def tshoot_pcap_action(self):
        pass

    def help_support_action(self):
        # Redirect to https://meraki.cisco.com/support
        pass

    def help_about_action(self):
        # Talk about yourself
        # Also, pre-alpha, version -1
        # Apache License
        pass

    def select_network(self):
        # If they select an organization name, org_links maps that to the URL
        org_name = self.Organizations.currentText()
        org_url = self.org_links[org_name]
        self.browser.open(org_url)

    def attempt_connection(self):
        # This is where OS-specific code will go
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
    main_window = MainWindow(login_window.get_browser())
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
