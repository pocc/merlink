#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls
import sys
from PyQt5.QtWidgets import QApplication, QTextEdit, QWidget, QPushButton, QVBoxLayout, QLabel


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.instructions = QLabel("Please enter your Meraki Dashboard username & password:")
        self.username = QTextEdit(self)
        self.password = QTextEdit(self)
        self.connect_btn = QPushButton("Connect")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.instructions)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.connect_btn)

        self.connect_btn.clicked.connect(self.make_connection)

        self.setLayout(layout)
        self.setWindowTitle('Meraki Client VPN')

        self.show()

    def make_connection(self):
        # This is where OS-specific code will go
        pass


app = QApplication(sys.argv)
writer = MainWindow()
# sys.exit(app.exec_()) # this causes errors on linux
app.exec()
