#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls
import sys
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QPushButton, QVBoxLayout, QLabel


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
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
        self.heading = QLabel("Client VPN Login")
        self.heading.setStyleSheet(self.heading_style)
        self.username_lbl = QLabel("Email")
        self.username_lbl.setStyleSheet(self.label_style)
        self.username = QLineEdit(self)
        self.password_lbl = QLabel("Password")
        self.password_lbl.setStyleSheet(self.label_style)
        self.password = QLineEdit(self)
        self.connect_btn = QPushButton("Connect")

        self.init_ui()

    def init_ui(self):
        VLayout = QVBoxLayout()
        VLayout.addWidget(self.heading)
        VLayout.addWidget(self.username_lbl)
        VLayout.addWidget(self.username)
        VLayout.addWidget(self.password_lbl)
        VLayout.addWidget(self.password)
        VLayout.addWidget(self.connect_btn)
        # Should prevent users from decreasing the size of the window past the minimum
        VLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        # Add a stretch so that all elements are at the top, regardless of user resizes
        VLayout.addStretch()

        self.connect_btn.clicked.connect(self.make_connection)

        self.setLayout(VLayout)
        self.setWindowTitle('Meraki Client VPN')

        self.show()

    def make_connection(self):
        # This is where OS-specific code will go
        pass


app = QApplication(sys.argv)
writer = MainWindow()
# sys.exit(app.exec_()) # this causes errors on linux
app.exec()
