# Utilities
import sys
import webbrowser

# Qt5
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QSystemTrayIcon, QTextEdit, QLineEdit, qApp,
                             QVBoxLayout, QComboBox, QMainWindow, QAction, QDialog, QMessageBox, QSpinBox, QMenu,
                             QStatusBar, QFrame, QListWidget, QListWidgetItem, QCheckBox, QHBoxLayout, QRadioButton)
from PyQt5.QtGui import QIcon, QFont

# Web Scraping

# OS modules
import subprocess
from os import getcwd, system

# Import the login_window file
from src.modules.pyinstaller_path_helper import resource_path
from src.gui.modal_dialogs import show_error_dialog, \
    show_feature_in_development_dialog
from src.modules.vpn_connection import VpnConnection
from src.modules.troubleshoot_vpn_failure import TroubleshootVpnFailure
from src.gui.login_window import LoginWindow

DEBUG = True


class MainWindow(QMainWindow):
    # Pass in browser_session object from LoginWindow so that we can maintain the same session
    # ASSERT: User has logged in and has a connection to Dashboard AND DNS is working
    def __init__(self):
        super(MainWindow, self).__init__()

        login_dialog = LoginWindow()
        # QDialog has two return values: Accepted and Rejected
        # login_window.exec_() will execute while we keep on getting Rejected
        if login_dialog.exec_() == QDialog.Accepted:
            self.browser = login_dialog.get_browser()
            self.username = login_dialog.username
            self.password = login_dialog.password

        if DEBUG:
            print("Main Window")

        """
        # Shelving this code as it prevents creating multiple processes using an IDE 
        if is_online():
            error_dialog('ERROR: You already have a running instance of merlink!'
                         '\nThis application will now close.')
            self.close()  # In lieu of sys.exit(app.exec_())
        """

        # Variables
        self.platform = sys.platform
        self.network_admin_only = False
        self.current_org_index = 0  # By default, we choose the first org to display
        self.org_qty = 0  # By default, you have access to 0 orgs
        # Initialize organization dictionary {Name: Link} and list for easier access. org_list is org_links.keys()
        self.org_links = {}
        self.org_list = []
        self.cwd = getcwd()  # get current working directory. We use cwd in multiple places, so fetch it once
        self.validation_list = QListWidget()

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

        self.scrape_orgs()
        self.main_init_ui()
        self.menu_bars()

    def change_organization(self):
        if self.org_dropdown.currentIndex() != 0:  # We only care if they've actually selected an organization
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

    def tshoot_vpn_fail_gui(self):
        self.status.showMessage("Status: Verifying configuration for " + self.current_network + "...")
        result = TroubleshootVpnFailure(self.fw_status_text, self.client_vpn_text,
                                        self.current_ddns, self.current_primary_ip)
        has_passed_validation = result.get_test_results()
        validation_textlist = [
            "Is the MX online?",
            "Can the client ping the firewall's public IP?",
            "Is the user behind the firewall?",
            "Is Client VPN enabled?",
            "Is authentication type Meraki Auth?",
            "Are UDP ports 500/4500 port forwarded through firewall?"]
        # "Is the user authorized for Client VPN?",
        for i in range(len(validation_textlist)):  # For as many times as items in the validation_textlist
            item = QListWidgetItem(validation_textlist[i])  # Initialize a QListWidgetItem out of a string
            self.validation_list.addItem(item)  # Add the item to the QListView

        for i in range(len(validation_textlist)):
            print("has passed" + str(i) + str(has_passed_validation[i]))
            if has_passed_validation[i]:
                self.validation_list.item(i).setIcon(QIcon(resource_path('src/media/checkmark-16.png')))
            else:
                self.validation_list.item(i).setIcon(QIcon(resource_path('src/media/x-mark-16.png')))

            # All the error messages! Once we know what the error dialog landscape looks like down here,
            # we might want to turn this into an error method with params

        self.status.showMessage("Status: Ready to connect to " + self.current_network + ".")

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

        # We don't need to change organization if the user chooses "-- Select an Organization --"

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

    @staticmethod
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
        show_feature_in_development_dialog()
        pass

    def file_save_action(self):
        # Might use this to save a vpn config
        show_feature_in_development_dialog()
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
        show_feature_in_development_dialog()
        pass

    def view_routing_action(self):
        # If linux/macos > netstat -rn
        # If Windows > route print
        show_feature_in_development_dialog()
        pass

    def view_data_action(self):
        show_feature_in_development_dialog()
        pass

    def tshoot_error_action(self):
        # In Windows, use powershell: get-eventlog
        show_feature_in_development_dialog()
        pass

    def tshoot_pcap_action(self):
        show_feature_in_development_dialog()
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
        # If they've selected organization and network
        if 'Select' not in self.org_dropdown.currentText() and 'Select' not in self.network_dropdown.currentText():
            # Get current network from dropdown
            network_name = self.network_dropdown.currentText()
            # Set VPN name to the network name +/- cosmetic things
            vpn_name = network_name.replace('- appliance', '') + '- VPN'

            if self.radio_dashboard_admin_user.isChecked() == 0:  # If the user is logging in as a guest user
                self.username = self.radio_username_textfield.text()
                self.password = self.radio_password_textfield.text()

            # Change status to reflect we're connecting. For fast connections, you might not see this message
            self.status.showMessage('Status: Connecting...')
            # Send a list to attempt_connection containing data from all the textboxes and spinboxes

            # Create VPN connection
            vpn_data = [
                vpn_name,
                self.current_ddns,
                self.psk,
                self.username,
                self.password
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
                successful_attempt = connection.attempt_windows_vpn(windows_options)

            elif self.platform == 'darwin':
                macos_options = []
                successful_attempt = connection.attempt_macos_vpn(macos_options)

            elif self.platform.startswith('linux'):  # linux, linux2 are both valid
                linux_options = []
                successful_attempt = connection.attempt_linux_vpn(linux_options)

            else:
                successful_attempt = False

            if successful_attempt:
                self.communicate_vpn_success()
            else:
                self.communicate_vpn_failure()

        else:  # They haven't selected an item in one of the message boxes
            show_error_dialog('You must select BOTH an organization AND network before connecting!')

    def communicate_vpn_success(self):
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

    def communicate_vpn_failure(self):
        self.is_connected = False
        self.status.showMessage('Status: Connection Failed')
        self.error_dialog("Connection Failed")
        self.tray_icon.setIcon(QIcon(resource_path('src/media/unmiles.ico')))
        self.troubleshoot_connection()

    @staticmethod
    def troubleshoot_connection(self):
        print("ACTIVELY troubleshooting connection")
        show_error_dialog('VPN Connection Failed!')

    def disconnect(self):
        if self.is_vpn_connected():
            system('rasdial ' + self.vpn_name + ' /disconnect')
        else:
            show_error_dialog("ERROR: You cannot disconnect if you are not connected!")

    def is_vpn_connected(self):
        if self.platform == 'win32':
            rasdial_status = subprocess.Popen(['rasdial'], stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
            return 'Connected to' in rasdial_status
        elif self.platform == 'darwin':
            pass
        elif self.platform.startswith('linux'):
            pass

    @staticmethod
    def get_debug_status():
        return DEBUG

