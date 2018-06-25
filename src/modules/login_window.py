#!/usr/bin/python3
from PyQt5.QtWidgets import (QLineEdit, QWidget, QPushButton, QLabel, QSpinBox, QCheckBox,
                             QVBoxLayout, QHBoxLayout, QDialog, QMessageBox, QDialogButtonBox)
from PyQt5.QtGui import QPixmap
import mechanicalsoup

from src.modules.pyinstaller_path_helper import resource_path
from src.modules.modal_dialogs import error_dialog


class LoginWindow(QDialog):
    def __init__(self):
        super(LoginWindow, self).__init__()

        self.meraki_img = QLabel('<a href=https://meraki.cisco.com/products/wireless#mr-new>MR advertisement</a>')
        self.meraki_img.setOpenExternalLinks(True)
        # self.meraki_img.l label.connect(open_new("https://meraki.cisco.com/products/wireless#mr-new")
        # mx-new: https://meraki.cisco.com/products/appliance#mx-new
        # sm-new: https://meraki.cisco.com/products/systems-manager#sm-new

        # Copying style from Dashboard Login (https://account.meraki.com/login/dashboard_login)
        self.heading_style = "font-family: verdana, sans-serif; font-style: normal; " \
                             "font-size: 28px; font-weight: 300; color:  #606060;"
        self.label_style = "font-family: verdana, sans-serif; font-style: normal; " \
                           "font-size: 13px; color: #606060;"
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
        layout_login.addLayout(layout_login_options)
        layout_login.addStretch()
        layout_login.addWidget(self.about_lbl)

        self.meraki_img.setPixmap(QPixmap(resource_path('src/media/new-mr.jpg')))

        # Background for program will be #Meraki green = #78be20
        self.setStyleSheet("background-color:#eee")
        layout_main = QHBoxLayout()
        layout_main.addWidget(login_widget)
        layout_main.addWidget(self.meraki_img)
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
        if '/login/login' in self.result_url:  # URL contains /login/login if login failed
            # Error message popup that will take control and that the user will need to acknowledge
            error_dialog('ERROR: Invalid username or password.')

            # Sanitize password field so they can reenter credentials
            ''' Design choice: Don't reset username as reentering can be annyoying if only password is wrong
                self.username_field.setText('')'''
            self.password_field.setText('')

            # Don't return 'Rejected' as value from QDialog object as that will kill login window for auth fail
            # self.reject()
        elif 'sms_auth' in self.result_url:  # Two-Factor redirect: https://account.meraki.com/login/sms_auth?go=%2F
            # QDialog that gets 6 digit two-factor code
            self.twofactor_dialog = QDialog()
            self.twofactor_dialog.setWindowTitle("Two-Factor Authentication")
            dialog_layout = QVBoxLayout()
            twofactor_code_layout = QHBoxLayout()
            self.twofactor_code_label = QLabel("Enter verification code")
            self.get_twofactor_code = QLineEdit()

            # Remember choice doesn't quite work yet
            # self.get_remember_choice = QCheckBox("Remember verification for this computer for 30 days.")

            self.twofactor_dialog_yesno = QHBoxLayout()
            yesbutton = QPushButton("Verify")
            yesbutton.setToolTip("Attempt connection with this two-factor code")
            nobutton = QPushButton("Cancel")
            yesbutton.setToolTip("Quit")
            self.twofactor_dialog_yesno.addWidget(yesbutton)
            self.twofactor_dialog_yesno.addWidget(nobutton)

            # Layout code
            twofactor_code_layout.addWidget(self.twofactor_code_label)
            twofactor_code_layout.addWidget(self.get_twofactor_code)
            dialog_layout.addLayout(twofactor_code_layout)
            # dialog_layout.addWidget(self.get_remember_choice)
            dialog_layout.addLayout(self.twofactor_dialog_yesno)
            self.twofactor_dialog.setLayout(dialog_layout)

            # self.twofactor_dialog.setModal(True)  # Forces you to interact with the dialog (desired behavior)
            yesbutton.clicked.connect(self.submit_twofactor_info)  # wait on user to submit information to go here
            nobutton.clicked.connect(self.quit_dialog)  # wait on user to submit information to go here
            self.twofactor_dialog.exec_()

        else:
            self.accept()

    def submit_twofactor_info(self):
        form = self.browser.select_form()
        self.browser["code"] = self.get_twofactor_code.text()
        # if self.get_remember_choice.isChecked():
            # self.browser["remember"] = "1"  # Set remember to checked by default
        form.choose_submit('commit')  # Click 'Verify' button
        self.browser.submit_selected()

        current_page = self.browser.get_current_page().text
        twofactor_success = current_page.find("Invalid verification code")  # Will return -1 if it is not found
        if twofactor_success == -1:  # if success
            self.quit_dialog()  # Kill the dialog because we don't need it any longer
            self.accept()
        else:
            error_dialog('ERROR: Invalid verification code')
            self.attempt_login()  # Try again. There is a recursion risk here.

    # Return browser with any username, password, and cookies with it
    def get_browser(self):
        return self.browser

    def quit_dialog(self):
        self.twofactor_dialog.close()
