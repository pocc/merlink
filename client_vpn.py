#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls
import sys
from PyQt5.QtWidgets import (QApplication, QLineEdit, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QPixmap


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.meraki_img = QLabel()

        # Copying style from Dashboard Login (https://account.meraki.com/login/dashboard_login)
        self.heading_style = "font-family: verdana, sans-serif; font-style: normal; " \
                             "font-size: 28px;" \
                             "font-weight: 300;" \
                             "color:  #666;" \
                             "background: #eee"
        self.label_style = "font-family: verdana, sans-serif; font-style: normal; " \
                           "font-size: 13px; " \
                           "color: #000; " \
                           "background: #eee;"
        self.heading = QLabel("Dashboard Login")
        self.heading.setStyleSheet(self.heading_style)
        self.username_lbl = QLabel("Email")
        self.username_lbl.setStyleSheet(self.label_style)
        self.username = QLineEdit(self)
        self.password_lbl = QLabel("Password")
        self.password_lbl.setStyleSheet(self.label_style)
        self.password = QLineEdit(self)
        self.connect_btn = QPushButton("Log in")
        self.forgot_password = QLabel("I forgot my password")
        self.forgot_password.setStyleSheet(self.label_style)
        self.create_account = QLabel("Create an account")
        self.create_account.setStyleSheet(self.label_style)

        self.init_ui()

    def init_ui(self):
        layout_login_options = QHBoxLayout()
        layout_login_options.addWidget(self.forgot_password)
        layout_login_options.addStretch()
        layout_login_options.addWidget(self.create_account)

        layout_login = QVBoxLayout()
        layout_login.addWidget(self.heading)
        layout_login.addWidget(self.username_lbl)
        layout_login.addWidget(self.username)
        layout_login.addWidget(self.password_lbl)
        layout_login.addWidget(self.password)
        layout_login.addWidget(self.connect_btn)
        # Should prevent users from decreasing the size of the window past the minimum
        layout_login.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        # Add a stretch so that all elements are at the top, regardless of user resizes
        layout_login.addStretch()
        layout_login.addLayout(layout_login_options)

        self.meraki_img.setPixmap(QPixmap('meraki_connections.png'))
        layout_main = QHBoxLayout()
        layout_main.addWidget(self.meraki_img)
        layout_main.addLayout(layout_login)

        self.connect_btn.clicked.connect(self.make_connection)

        self.setLayout(layout_main)
        self.setWindowTitle('Meraki Client VPN')

        self.show()

    def make_connection(self):
        # This is where OS-specific code will go
        pass


app = QApplication(sys.argv)
window = MainWindow()
# sys.exit(app.exec_()) # this causes errors on linux
app.exec()
