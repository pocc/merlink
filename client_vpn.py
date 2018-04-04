#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls
import sys
import time
from PyQt5.QtWidgets import (QApplication, QLineEdit, QWidget, QPushButton, QLabel,
                             QVBoxLayout, QHBoxLayout, QComboBox)
from PyQt5.QtGui import QPixmap


class LoginWindow(QWidget):
    def __init__(self):
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
        self.username = QLineEdit(self)
        self.password_lbl = QLabel("Password")
        self.password_lbl.setStyleSheet(self.label_style)
        self.password = QLineEdit(self)
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
        layout_login.addWidget(self.username)
        layout_login.addWidget(self.password_lbl)
        layout_login.addWidget(self.password)
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
        self.login_btn.clicked.connect(self.attempt_login)

        self.setLayout(layout_main)
        self.setWindowTitle('Meraki Client VPN')

        self.show()

    def attempt_login(self):
        # ACTUALLY attempt to login
        self.close()
        # Call an object in the other class to continue
        init_main_window = MainWindow()
        init_main_window()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.init_ui()
        self.attempt_connection()

        self.show()

    def init_ui(self):

        self.setWindowTitle('Meraki Client VPN: Main')
        self.Organizations = QComboBox()
        # List of lorem ipsum organizations
        self.Organizations.addItems({"Wonka Industries", "Acme Corp.", "Stark Industries", "Wayne Enterprises", "Hooli"})
        self.Networks = QComboBox()
        self.Networks.addItems({"Atlantis", "Gotham City", "Metropolis", "Rivendell", "Coruscant"})
        self.Organizations.setCurrentText("Acme Corp.")
        self.Networks.setCurrentText("Gotham City")
        vert_layout = QVBoxLayout()
        vert_layout.addWidget(self.Organizations)
        vert_layout.addWidget(self.Networks)
        vert_layout.addStretch()
        self.setLayout(vert_layout)

    def attempt_connection(self):
        # This is where OS-specific code will go
        pass

app = QApplication(sys.argv)
window = LoginWindow()
# sys.exit(app.exec_()) # this causes warnings on linux
app.exec()
