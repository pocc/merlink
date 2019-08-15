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
"""Functions that take a Qt object and decorate it like a cake.

This file exists to take much of the UI content of the MainWindow and
LoginDialog classes so that the Qt elements in this project are more
properly segmented off. This is in lieu of having created the UI files in
Qt Designer, converted them to pyuic, and then never touched the UI
files again (not a route I chose to go).

Args (for any function):
    app (Qt Object): The window/dialog object that this function decorates.
"""
import webbrowser
import sys

from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QFont
from PyQt5.Qt import QPixmap

from merlink.os_utils import open_vpnsettings
from merlink.os_utils import pyinstaller_path


class LoginWindowUi:
    """This class manages the system tray icon of the main program, post-login.
    Attributes:
        app (QMainWindow): Set to MainWindow object (required binding for Qt)
    """

    def __init__(self, app):
        self.app = app
        self.login_widget_setup()
        self.login_window_setup()
        self.login_set_layout()

    def login_widget_setup(self):
        """Take login self.app.and add widgets to it."""
        # Copying style from Dashboard Login
        # (https://account.meraki.com/login/dashboard_login)
        self.app.heading_style = \
            "font-family: verdana, sans-serif; font-style: normal; font-size" \
            ": 28px; font-weight: 300; color:  #606060;"
        self.app.label_style = "font-family: verdana, sans-serif; font-style" \
                               ": normal; font-size: 13px; color: #606060;"
        self.app.link_style = "font-family: verdana, sans-serif; font-style:" \
                              " normal; font-size: 13px; color: #1795E6;"
        self.app.heading = QLabel("Dashboard Login")
        self.app.heading.setStyleSheet(self.app.heading_style)
        self.app.username_lbl = QLabel("Email")
        self.app.username_lbl.setStyleSheet(self.app.label_style)
        self.app.password_lbl = QLabel("Password")
        self.app.password_lbl.setStyleSheet(self.app.label_style)
        self.app.username_field = QLineEdit(self.app)
        self.app.password_field = QLineEdit(self.app)
        # Reset password field to '', especially if login failed
        self.app.password_field.setText('')
        # Masks password as a series of dots instead of characters
        self.app.password_field.setEchoMode(QLineEdit.Password)
        self.app.login_btn = QPushButton("Log in")

        # self.app.login_btn.setStyleSheet(self.app.login_btn_style)
        self.app.forgot_password_lbl = \
            QLabel("<a href=\"https://account.meraki.com/login/reset_password"
                   "\" style=\"color:#1795E6;text-decoration:none\">"
                   "I forgot my password</a>")
        self.app.forgot_password_lbl.setStyleSheet(self.app.link_style)
        self.app.forgot_password_lbl.setOpenExternalLinks(True)
        self.app.create_account_lbl = \
            QLabel(" <a href=\"https://account.meraki.com/login/signup\" "
                   "style=\"color:#1795E6;text-decoration:none\">"
                   "Create an account</a>")
        self.app.create_account_lbl.setStyleSheet(self.app.link_style)
        self.app.create_account_lbl.setOpenExternalLinks(True)
        self.app.about_lbl = \
            QLabel("<a href=\"https://github.com/pocc/merlink\" style=\""
                   "color:#1795E6;text-decoration:none\">About</a>")
        self.app.about_lbl.setStyleSheet(self.app.link_style)
        self.app.about_lbl.setOpenExternalLinks(True)

        # Set up username and password so these vars have values
        self.app.username = ''
        self.app.password = ''

    def login_window_setup(self):
        """Set options for the login window self.app."""
        self.app.setModal(True)  # Make the login window prevent program usage
        self.app.meraki_img = QLabel()
        self.app.meraki_img.setOpenExternalLinks(True)
        pixmap = QPixmap(pyinstaller_path('media/cloud_miles.png'))
        self.app.meraki_img.setPixmap(pixmap)
        # Background for program should be #Meraki green = #78be20
        self.app.setStyleSheet("background-color:#eee")
        self.app.setWindowTitle('MerLink - Login Window')

    def login_set_layout(self):
        """Tie login layout to QDialog object."""
        layout_login_options = QHBoxLayout()
        layout_login_options.addWidget(self.app.forgot_password_lbl)
        layout_login_options.addStretch()
        layout_login_options.addWidget(self.app.create_account_lbl)

        # Create a widget to contain the login layout.
        # This allows us to paint the background of the widget
        login_widget = QWidget(self.app)
        login_widget.setStyleSheet("background-color:#fff")
        # Create labels and textboxes to form a login layout
        layout_login = QVBoxLayout(login_widget)
        layout_login.addStretch()
        layout_login.addWidget(self.app.heading)
        layout_login.addWidget(self.app.username_lbl)
        layout_login.addWidget(self.app.username_field)
        layout_login.addWidget(self.app.password_lbl)
        layout_login.addWidget(self.app.password_field)
        layout_login.addWidget(self.app.login_btn)
        layout_login.addLayout(layout_login_options)
        layout_login.addStretch()
        layout_login.addStretch()
        layout_login.addWidget(self.app.about_lbl)

        layout_main = QHBoxLayout()
        layout_main.addWidget(login_widget)
        layout_main.addWidget(self.app.meraki_img)
        self.app.setLayout(layout_main)


class TfaDialogUi:
    """This class manages the system tray icon of the main program, post-login.
    Attributes:
        app (QMainWindow): Set to MainWindow object (required binding for Qt)
    """

    def __init__(self, app):
        self.app = app
        self.login_tfa_set_layout()
        self.tfa_widget_setup()
        self.tfa_set_layout()

    def login_tfa_set_layout(self):
        """Set the layout for the tfa dialog."""
        # Required to have this class variables as it is not possible to
        # return/pass values to/from triggered functions (self.app.tfa_verify)
        self.app.get_twofactor_code = QLineEdit()
        self.app.twofactor_dialog = QDialog()

    def tfa_widget_setup(self):
        """Set up the two-factor dialog UI."""
        self.app.get_twofactor_code.clear()  # Clear if exists
        # QDialog that gets 6 digit two-factor code
        self.app.twofactor_dialog.setWindowTitle("Two-Factor Authentication")

        self.app.twofactor_code_label = QLabel("Enter verification code")
        self.app.twofactor_dialog_yesno = QHBoxLayout()
        self.app.yesbutton = QPushButton("Verify")
        self.app.yesbutton.setToolTip("Attempt connection with this tfa code")
        self.app.nobutton = QPushButton("Cancel")
        self.app.yesbutton.setToolTip("Quit")
        self.app.twofactor_dialog_yesno.addWidget(self.app.yesbutton)
        self.app.twofactor_dialog_yesno.addWidget(self.app.nobutton)

    def tfa_set_layout(self):
        """Set up the TFA layout."""
        # Layout code
        dialog_layout = QVBoxLayout()
        twofactor_code_layout = QHBoxLayout()
        twofactor_code_layout.addWidget(self.app.twofactor_code_label)
        twofactor_code_layout.addWidget(self.app.get_twofactor_code)
        dialog_layout.addLayout(twofactor_code_layout)
        # dialog_layout.addWidget(self.app.get_remember_choice)
        dialog_layout.addLayout(self.app.twofactor_dialog_yesno)
        self.app.twofactor_dialog.setLayout(dialog_layout)


class MainWindowUi:
    """This class manages the system tray icon of the main program, post-login.
    Attributes:
        app (QMainWindow): Set to MainWindow object (required binding for Qt)
    """

    def __init__(self, app):
        self.app = app
        self.main_window_widget_setup()
        self.main_window_user_auth_setup()
        self.main_window_vpn_vars_setup()
        self.main_window_set_layout()
        self.main_window_set_admin_layout()

    def main_window_widget_setup(self):
        """Set up the main window object and org/net dropdowns."""
        # QMainWindow requires that a central app be set
        self.app.cw = QWidget(self.app)
        self.app.setCentralWidget(self.app.cw)
        # Set minimum width of Main Window to 500 pixels
        self.app.cw.setMinimumWidth(500)
        self.app.setWindowTitle('MerLink - VPN Client for Meraki firewalls')
    
        # Create org and network dropdowns so the user can select the firewall
        # they would like to connect to.
        self.app.org_dropdown = QComboBox()
        self.app.org_dropdown.addItem('-- Select an Organization --')
        self.app.network_dropdown = QComboBox()
        self.app.network_dropdown.setEnabled(False)

    def main_window_user_auth_setup(self):
        """Set initial vars for user/pass fields for dasboard/guest user."""
        self.app.radio_username_label = QLabel("Email")
        self.app.radio_username_label.setStyleSheet("color: #606060")  # Gray
        self.app.radio_username_textfield = QLineEdit()
        self.app.radio_password_label = QLabel("Password")
        self.app.radio_password_label.setStyleSheet("color: #606060")  # Gray
        self.app.radio_password_textfield = QLineEdit()
        self.app.radio_password_textfield.setEchoMode(QLineEdit.Password)
    
        self.app.user_auth_section = QVBoxLayout()
        self.app.radio_user_layout = QHBoxLayout()
        self.app.user_auth_section.addLayout(self.app.radio_user_layout)
        self.app.radio_admin_user = QRadioButton("Dashboard Admin")
        # Default is to have dashboard user
        self.app.radio_admin_user.setChecked(True)
        self.app.radio_guest_user = QRadioButton("Guest User")
        self.app.radio_user_layout.addWidget(self.app.radio_admin_user)
        self.app.radio_user_layout.addWidget(self.app.radio_guest_user)
        self.app.user_auth_section.addWidget(self.app.radio_username_label)
        self.app.user_auth_section.addWidget(self.app.radio_username_textfield)
        self.app.user_auth_section.addWidget(self.app.radio_password_label)
        self.app.user_auth_section.addWidget(self.app.radio_password_textfield)
    
    def main_window_vpn_vars_setup(self):
        """Set up the vpn vars UI region."""
        # Allow the user to change the VPN name
        self.app.vpn_name_layout = QHBoxLayout()
        self.app.vpn_name_label = QLabel("VPN Name:")
        self.app.vpn_name_textfield = QLineEdit()
        self.app.vpn_name_layout.addWidget(self.app.vpn_name_label)
        self.app.vpn_name_layout.addWidget(self.app.vpn_name_textfield)
    
        # Ask the user for int/str values if they want to enter them
        self.app.idle_disconnect_layout = QHBoxLayout()
        self.app.idle_disconnect_chkbox = QCheckBox("Idle disconnect seconds?")
        self.app.idle_disconnect_spinbox = QSpinBox()
        self.app.idle_disconnect_spinbox.setValue(0)
        # Negative seconds aren't useful here
        self.app.idle_disconnect_spinbox.setMinimum(0)
        self.app.idle_disconnect_layout.addWidget(self.app.idle_disconnect_chkbox)
        self.app.idle_disconnect_layout.addWidget(self.app.idle_disconnect_spinbox)
    
        self.app.dns_suffix_layout = QHBoxLayout()
        self.app.dns_suffix_chkbox = QCheckBox("DNS Suffix?")
        self.app.dns_suffix_txtbox = QLineEdit('-')
        self.app.dns_suffix_layout.addWidget(self.app.dns_suffix_chkbox)
        self.app.dns_suffix_layout.addWidget(self.app.dns_suffix_txtbox)
    
        # Boolean asks of the user
        self.app.split_tunneled_chkbox = QCheckBox("Split-Tunnel?")
        self.app.remember_credential_chkbox = QCheckBox("Remember Credentials?")
        self.app.use_winlogon_chkbox = QCheckBox("Use Windows Logon Credentials?")
    
        self.app.connect_btn = QPushButton("Connect")
    
        # Status bar setup
        # Create a horizontal line above the status bar to highlight it
        self.app.hline = QFrame()
        self.app.hline.setFrameShape(QFrame.HLine)
        self.app.hline.setFrameShadow(QFrame.Sunken)
        # Status bar be at bottom and inform user of what the program is doing.
        self.app.status = QStatusBar()
        self.app.status.showMessage("Status: Select organization")
        self.app.status.setStyleSheet("Background: white")

    def main_window_set_layout(self):
        """Create a main vertical layout that may contain other layouts."""
        vert_layout = QVBoxLayout()
        vert_layout.addWidget(self.app.org_dropdown)
        vert_layout.addWidget(self.app.network_dropdown)
        vert_layout.addLayout(self.app.user_auth_section)
        vert_layout.addLayout(self.app.vpn_name_layout)
    
        # Add layouts for specialized params
        vert_layout.addLayout(self.app.idle_disconnect_layout)
        vert_layout.addLayout(self.app.dns_suffix_layout)
    
        # Add checkboxes
        vert_layout.addWidget(self.app.split_tunneled_chkbox)
        vert_layout.addWidget(self.app.remember_credential_chkbox)
        vert_layout.addWidget(self.app.use_winlogon_chkbox)
    
        # Add stuff at bottom
        vert_layout.addWidget(self.app.connect_btn)
        vert_layout.addWidget(self.app.hline)
        vert_layout.addWidget(self.app.status)
    
        # Tie main layout to central window object (REQUIRED)
        self.app.cw.setLayout(vert_layout)
    
    def main_window_set_admin_layout(self):
        """Set the dashboard user layout.
    
        Hides guest user layout as we will only be connecting with one user.
        The user will see the username/obfuscated password they entered.
        """
        self.app.radio_username_textfield.setText(
            self.app.login_dict['username'])
        self.app.radio_username_textfield.setReadOnly(True)
        self.app.radio_password_textfield.setText(
            self.app.login_dict['password'])
        self.app.radio_password_textfield.setReadOnly(True)

    def main_window_set_guest_layout(self):
        """Set the guest user layout.
    
        Hides dashboard user layout as we will only be connecting with one user.
        The user will see blank user/pass text fields where they can enter
        information for a guest user.
        """
        self.app.radio_username_textfield.clear()
        self.app.radio_username_textfield.setReadOnly(False)
        self.app.radio_password_textfield.clear()
        self.app.radio_password_textfield.setReadOnly(False)


class SystrayIconUi:
    """This class manages the system tray icon of the main program, post-login.
    Attributes:
        app (QMainWindow): Set to MainWindow object (required binding for Qt)
        tray_icon (QSystemTrayIcon): System Tray object that has all of the
          functionality that this class requires.
    """

    def __init__(self, app):
        """Init QSystemTrayIcon and set the Window and Tray Icons."""
        self.app = app
        self.app.setWindowIcon(QIcon(pyinstaller_path('media/miles.ico')))
        self.tray_icon = QSystemTrayIcon(app)
        self.tray_icon.setIcon(QIcon(pyinstaller_path('media/miles.ico')))
        connection_status = 'VPN disconnected'
        self.tray_icon.setToolTip("Merlink - " + connection_status)

        connect_action = QAction("Connect to ...", app)
        # These 3 lines are to make "Connect to ..." bold
        font = QFont()
        font.setBold(True)
        connect_action.setFont(font)

        disconnect_action = QAction("Disconnect", app)
        show_action = QAction("Show", app)
        quit_action = QAction("Exit", app)
        hide_action = QAction("Hide", app)
        # Allow this if we're not connected
        connect_action.triggered.connect(app.setup_vpn)
        disconnect_action.triggered.connect(app.disconnect)
        show_action.triggered.connect(app.show)
        hide_action.triggered.connect(app.hide)
        quit_action.triggered.connect(sys.exit)

        tray_menu = QMenu()
        tray_menu.addAction(connect_action)
        tray_menu.addAction(disconnect_action)
        tray_menu.addSeparator()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # If systray icon is clicked
        # If they click on the connected message, show them the VPN connection
        self.tray_icon.activated.connect(self.icon_activated)

    def icon_activated(self, reason):
        """Respond to the user has clicking on the systray icon.
        If single or double click, show the application
        If middle click, go to meraki.cisco.com
        Override closeEvent, to intercept the window closing event
        Args:
            reason (QSystemTrayIcon.ActivationReason): An enum of
              [0,4] of how the user interacted with the system tray
              ~
              More information on ActivationReasons can be found here:
              http://doc.qt.io/qt-5/qsystemtrayicon.html#ActivationReason-enum
        """
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.app.show()  # So it will show up in taskbar
            self.app.raise_()  # for macOS
            self.app.activateWindow()  # for Windows

        elif reason == QSystemTrayIcon.MiddleClick:
            # Open Meraki's homepage
            webbrowser.open("https://meraki.cisco.com/")

    def application_minimized(self):
        """Minimize the window."""
        self.tray_icon.showMessage("Merlink", "Merlink is now minimized",
                                   QSystemTrayIcon.Information, 1000)

    def set_vpn_failure(self):
        """Tell user that VPN connection was unsuccessful.
        Show an icon of Miles with a red interdictory circle and let
        the user know the connection failed.
        """
        self.tray_icon.setIcon(QIcon(pyinstaller_path(
            'media/unmiles.ico')))
        # Provide system VPN settings if the user wants more info
        self.tray_icon.messageClicked.connect(open_vpnsettings)
        # Show the user this message so they know where the program went
        self.tray_icon.showMessage("Merlink", "Connection failure!",
                                   QSystemTrayIcon.Information, 1500)

    def set_vpn_success(self):
        """Tell user that VPN connection was successful.
        NOTE: There's no such thing as "minimize to system tray".
        What we're doing is hiding the window and
        then adding an icon to the system tray
        This function will set the icon to Miles with 3D glasses and
        show a message that the connection was successful.
        """
        self.tray_icon.setIcon(
            QIcon(pyinstaller_path('media/connected_miles.ico')))
        # Provide system VPN settings if the user wants more info
        self.tray_icon.messageClicked.connect(open_vpnsettings)
        # Show the user this message so they know where the program went
        self.tray_icon.showMessage("Merlink", "Connection success!",
                                   QSystemTrayIcon.Information, 1500)


class MenuBarsUi:
    """Menubars of the GUI.
    This class contains mostly boilerplate Qt UI.
    Attributes:
        menu_bar (QMenuBar): The Main Window's built-in menu bar object
        file_menu (QAction): File menu
        edit_menu (QAction): Edit menu
        help_menu (QAction): Help menu
    """

    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self, menu_bar):
        """Initialize all of the program menus."""
        super(MenuBarsUi, self).__init__()
        self.menu_bar = menu_bar
        self.file_menu = menu_bar.addMenu('&File')
        self.edit_menu = menu_bar.addMenu('&Edit')
        self.help_menu = menu_bar.addMenu('&Help')

    def generate_menu_bars(self):
        """Create each of the menu bars.
        NOTE: Some of the menu additions here are planned features
        """
        # File options
        file_sysprefs = QAction('&Open VPN System Prefs', self.menu_bar)
        file_sysprefs.setShortcut('Ctrl+O')
        file_quit = QAction('&Quit', self.menu_bar)
        file_quit.setShortcut('Ctrl+Q')

        # Edit options
        edit_preferences = QAction('&Prefrences', self.menu_bar)
        edit_preferences.setShortcut('Ctrl+P')

        # Help options
        help_support = QAction('Get S&upport', self.menu_bar)
        help_support.setShortcut('Ctrl+U')
        help_about = QAction('A&bout', self.menu_bar)
        help_about.setShortcut('Ctrl+B')

        self.file_menu.addAction(file_sysprefs)
        self.file_menu.addAction(file_quit)
        self.edit_menu.addAction(edit_preferences)
        self.help_menu.addAction(help_about)

        file_sysprefs.triggered.connect(self.file_sysprefs)
        file_quit.triggered.connect(sys.exit)
        edit_preferences.triggered.connect(self.edit_prefs_action)
        help_about.triggered.connect(self.help_about_action)

    @staticmethod
    def file_sysprefs():
        """Open the system VPN settings.
        Raises:
            FileNotFoundError: If vpn settings are not found
        """
        try:
            open_vpnsettings()
        except FileNotFoundError as error:
            if sys.platform.startswith('linux'):
                show_error_dialog(
                    str(error) + '\n\nThis happens when gnome-network-manager '
                    'is not installed and vpn prefs are opened in linux.')
            else:
                show_error_dialog(
                    str(error) + '\n\nUnknown error: VPN '
                    'settings not found')

    @staticmethod
    def edit_prefs_action():
        """Show the preferences.
        Currently, it merely shows an HTML heading, but the hope is be able
        to control more settings from this pane.
        > It may be worthwhile to use a QSettings object here instead
        (http://doc.qt.io/qt-5/qsettings.html).
        """
        # Preferences should go here.
        # How many settings are here will depend on the feature set
        prefs = QDialog()
        layout = QVBoxLayout()
        prefs_heading = QLabel('<h1>Preferences</h1>')
        layout.addWidget(prefs_heading)
        prefs.setLayout(layout)
        prefs.show()

    @staticmethod
    def help_about_action():
        """Show an 'about' dialog containing the license."""
        about_popup = QDialog()
        about_popup.setWindowTitle("Meraki Client VPN: About")
        about_program = QLabel()
        about_program.setText("<h1>Meraki VPN Client 0.8.5</h1>\n"
                              "Developed by Ross Jacobs<br><br><br>"
                              "This project is licensed with the "
                              "Apache License, which can be viewed below:")
        license_text = open("LICENSE.txt").read()
        licenses = QTextEdit()
        licenses.setText(license_text)
        # People shouldn't be able to edit licenses!
        licenses.setReadOnly(True)
        popup_layout = QVBoxLayout()
        popup_layout.addWidget(about_program)
        popup_layout.addWidget(licenses)
        about_popup.setLayout(popup_layout)
        about_popup.setMinimumSize(600, 200)
        about_popup.exec_()


def show_error_dialog(message):
    """Show an error dialog with a message.

    This script contains multiple GUI modal dialogs:
    https://ux.stackexchange.com/questions/12045/what-is-a-modal-dialog-window

    "A modal dialog is a window that forces the user to interact with it
    before they can go back to using the parent application."

    Args:
        message (string): A message telling the user what is wrong.
    """
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setWindowTitle("Error!")
    error_dialog.setText(message)
    error_dialog.exec_()


def show_question_dialog(message):
    """Send the user a question and record their decision.

    Args:
        message (string): A question asking the user what they want to do.
    Returns:
        result (QDialog.DialogCode): Returns a QDialog code of Rejected (no) |
        Accepted (yes) depending on user input.

    """
    question_dialog = QMessageBox()
    question_dialog.setIcon(QMessageBox.Question)
    question_dialog.setWindowTitle("Error!")
    question_dialog.setText(message)
    question_dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    question_dialog.setDefaultButton(QMessageBox.Yes)
    decision = question_dialog.exec_()
    return decision


def show_feature_in_development_dialog():
    """Informs the user that something is a feature in development."""
    fid_message = QMessageBox()
    fid_message.setIcon(QMessageBox.Information)
    fid_message.setWindowTitle("Meraki Client VPN: Features in Progress")
    fid_message.setText('This feature is currently in progress.')
    fid_message.exec_()


def vpn_status_dialog(title, message):
    """Tells the user the status of the VPN connection.

    args:
        title (string): A window title to summarize the message.
        message (string): A message to give to the user.
    """
    success_message = QMessageBox()
    success_message.setIcon(QMessageBox.Information)
    success_message.setWindowTitle(title)
    success_message.setText(message)
    success_message.exec_()
