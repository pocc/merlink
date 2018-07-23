#!/usr/bin/python3

# ~ https://ux.stackexchange.com/questions/12045/what-is-a-modal-dialog-window
# "A modal dialog is a window that forces the user to interact with it
# before they can go back to using the parent application."


# Python modules
from PyQt5.QtWidgets import (QLineEdit, QWidget, QPushButton, QDialog,
                             QLabel, QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QPixmap

# Local modules
from src.modules.pyinstaller_path_helper import resource_path


class LoginDialog(QDialog):
    def __init__(self):
        super(LoginDialog, self).__init__()

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
        self.setWindowTitle('Meraki Client VPN')

        self.login_btn.clicked.connect(self.close)
        # Test connection with a virtual browser

    def get_login_info(self):
        return self.username_field.text(), self.password_field.text()

    def get_tfa_query(self):
        # QDialog that gets 6 digit two-factor code
        tfa_dialog = QDialog()
        tfa_dialog.setWindowTitle("Two-Factor Authentication")
        tfa_dialog_layout = QVBoxLayout()
        tfa_code_layout = QHBoxLayout()
        tfa_code_label = QLabel("Enter verification code")
        get_tfa_code = QLineEdit()

        # 'Remember choice' checkbox doesn't quite work yet
        # get_remember_choice = QCheckBox("Remember verification "
        #                                "for this computer for 30 days.")

        tfa_dialog_yesno = QHBoxLayout()
        yesbutton = QPushButton("Verify")
        yesbutton.setToolTip(
            "Attempt connection with this two-factor code")
        nobutton = QPushButton("Cancel")
        yesbutton.setToolTip("Quit")
        tfa_dialog_yesno.addWidget(yesbutton)
        tfa_dialog_yesno.addWidget(nobutton)

        # Layout code
        tfa_code_layout.addWidget(tfa_code_label)
        tfa_code_layout.addWidget(get_tfa_code)
        tfa_dialog_layout.addLayout(tfa_code_layout)
        # dialog_layout.addWidget(self.get_remember_choice)
        tfa_dialog_layout.addLayout(tfa_dialog_yesno)
        tfa_dialog.setLayout(tfa_dialog_layout)

        # Forces you to interact with the dialog (desired behavior)
        # `self.twofactor_dialog.setModal(True)`
        # Wait on user to submit information to go here
        yesbutton.clicked.connect(
            self.browser.tfa_submit_info(get_tfa_code.text()))
        # wait on user to submit information to go here
        nobutton.clicked.connect(tfa_dialog.close())
        tfa_dialog.exec_()

        if self.browser.get_tfa_success():  # if success
            # Kill the dialog because we don't need it any longer
            tfa_dialog.close()
            tfa_dialog.accept()

        else:
            self.show_error_dialog('ERROR: Invalid verification code')
            # Try again. There is a recursion risk here.
            self.browser.attempt_login()