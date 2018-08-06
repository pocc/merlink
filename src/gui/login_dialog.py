# coding=UTF-8
"""
    :parameter
    :returns
"""

# Python modules
from PyQt5.QtWidgets import (QLineEdit, QWidget, QPushButton, QDialog,
                             QLabel, QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QPixmap

# Local modules
from src.modules.pyinstaller_path_helper import resource_path
from src.modules.dashboard_browser import DataScraper
from src.gui.modal_dialogs import show_error_dialog


class LoginDialog(QDialog):
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self):
        super(LoginDialog, self).__init__()
        self.setModal(True)  # Make the login window prevent program usage

        self.browser = DataScraper()

        # LOGIN WINDOW UI SETUP
        self.meraki_img = QLabel('<a href=https://meraki.cisco.com/products/'
                                 'wireless#mr-new>MR advertisement</a>')
        self.meraki_img.setOpenExternalLinks(True)

        # Copying style from Dashboard Login
        # (https://account.meraki.com/login/dashboard_login)
        self.heading_style = "font-family: verdana, sans-serif; font-style: " \
                             "normal; font-size: 28px; font-weight: 300; " \
                             "color:  #606060;"
        self.label_style = "font-family: verdana, sans-serif; font-style: " \
                           "normal; font-size: 13px; color: #606060;"
        self.link_style = "font-family: verdana, sans-serif; font-style: " \
                          "normal; font-size: 13px; color: #1795E6;"

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

        # Reset password field to '', especially if login failed
        self.password_field.setText('')

        # Masks password as a series of dots instead of characters
        self.password_field.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Log in")

        # self.login_btn.setStyleSheet(self.login_btn_style)
        self.forgot_password_lbl = \
            QLabel("<a href=\"https://account.meraki.com/login/reset_password"
                   "\" style=\"color:#1795E6;text-decoration:none\">"
                   "I forgot my password</a>")
        self.forgot_password_lbl.setStyleSheet(self.link_style)
        self.forgot_password_lbl.setOpenExternalLinks(True)
        self.create_account_lbl = \
            QLabel(" <a href=\"https://account.meraki.com/login/signup\" "
                   "style=\"color:#1795E6;text-decoration:none\">"
                   "Create an account</a>")
        self.create_account_lbl.setStyleSheet(self.link_style)
        self.create_account_lbl.setOpenExternalLinks(True)
        self.about_lbl = \
            QLabel("<a href=\"https://github.com/pocc/merlink\" style=\""
                   "color:#1795E6;text-decoration:none\">About</a>")
        self.about_lbl.setStyleSheet(self.link_style)
        self.about_lbl.setOpenExternalLinks(True)

        layout_login_options = QHBoxLayout()
        layout_login_options.addWidget(self.forgot_password_lbl)
        layout_login_options.addStretch()
        layout_login_options.addWidget(self.create_account_lbl)

        # Create a widget to contain the login layout.
        # This allows us to paint the background of the widget
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

        self.meraki_img.setPixmap(
            QPixmap(resource_path('src/media/new-mr.jpg')))

        # Background for program will be #Meraki green = #78be20
        self.setStyleSheet("background-color:#eee")
        layout_main = QHBoxLayout()
        layout_main.addWidget(login_widget)
        layout_main.addWidget(self.meraki_img)
        self.setLayout(layout_main)
        self.setWindowTitle('MerLink')

        # TWOFACTOR_DIALOG UI SETUP #
        # QDialog that gets 6 digit two-factor code
        self.twofactor_dialog = QDialog()
        self.twofactor_dialog.setWindowTitle("Two-Factor Authentication")
        dialog_layout = QVBoxLayout()
        twofactor_code_layout = QHBoxLayout()
        self.twofactor_code_label = QLabel("Enter verification code")
        self.get_twofactor_code = QLineEdit()

        self.twofactor_dialog_yesno = QHBoxLayout()
        self.yesbutton = QPushButton("Verify")
        self.yesbutton.setToolTip("Attempt connection with this tfa code")
        self.nobutton = QPushButton("Cancel")
        self.yesbutton.setToolTip("Quit")
        self.twofactor_dialog_yesno.addWidget(self.yesbutton)
        self.twofactor_dialog_yesno.addWidget(self.nobutton)

        # Layout code
        twofactor_code_layout.addWidget(self.twofactor_code_label)
        twofactor_code_layout.addWidget(self.get_twofactor_code)
        dialog_layout.addLayout(twofactor_code_layout)
        # dialog_layout.addWidget(self.get_remember_choice)
        dialog_layout.addLayout(self.twofactor_dialog_yesno)
        self.twofactor_dialog.setLayout(dialog_layout)

        # INIT THIS OBJECT
        self.show_login()

    def show_login(self):
        self.show()
        self.login_btn.clicked.connect(self.check_login_attempt)
        # Test connection with a virtual browser

    def get_login_info(self):
        return self.username_field.text(), self.password_field.text()

    def get_browser(self):
        return self.browser

    """Keeping this code in here even though it is interface-independent.
    If we don't keep this here, then the login button will need to connect to
    self.close. It may look weird if the login window closes due to the user
    incorrectly entering user/pass and then reopens"""
    def check_login_attempt(self):
        result = self.browser.attempt_login(
            self.username_field.text(),
            self.password_field.text()
        )

        if result == 'auth_error':
            show_error_dialog('ERROR: Invalid username or password.')
            self.password_field.setText('')
        elif result == 'sms_auth':
            while not self.browser.get_tfa_success():
                self.get_tfa_dialog()
                if self.twofactor_dialog.result() == QDialog.Rejected:
                    break
        elif result == 'auth_success':
            self.close()
        else:
            show_error_dialog("ERROR: Invalid authentication type!")

    def get_tfa_dialog(self):
        self.yesbutton.clicked.connect(self.tfa_verify)
        self.nobutton.clicked.connect(self.tfa_cancel)
        self.twofactor_dialog.exec_()

    def tfa_verify(self):
        self.browser.tfa_submit_info(self.get_twofactor_code.text())
        if self.browser.get_tfa_success():
            self.twofactor_dialog.accept()
            self.close()
        else:
            show_error_dialog('ERROR: Invalid verification code')

    def tfa_cancel(self):
        self.twofactor_dialog.reject()
