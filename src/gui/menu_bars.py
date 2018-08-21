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

"""This class contains the menubars of the program."""
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTextEdit
import webbrowser

from src.gui.modal_dialogs import show_feature_in_development_dialog


class MenuBars:
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList
    def __init__(self, bar):
        super(MenuBars, self).__init__()
        self.bar = bar
        self.file_menu = bar.addMenu('&File')
        self.edit_menu = bar.addMenu('&Edit')
        self.view_menu = bar.addMenu('&View')
        self.tshoot_menu = bar.addMenu('&Troubleshoot')
        self.help_menu = bar.addMenu('&Help')

    def generate_menu_bars(self):
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        # File options
        file_open = QAction('&Open', self.bar)
        file_open.setShortcut('Ctrl+O')
        file_save = QAction('&Save', self.bar)
        file_save.setShortcut('Ctrl+S')
        file_quit = QAction('&Quit', self.bar)
        file_quit.setShortcut('Ctrl+Q')

        # Edit options
        edit_preferences = QAction('&Prefrences', self.bar)
        edit_preferences.setShortcut('Ctrl+P')

        # View options
        view_interfaces = QAction('&Interfaces', self.bar)
        view_interfaces.setShortcut('Ctrl+I')
        view_routing = QAction('&Routing', self.bar)
        view_routing.setShortcut('Ctrl+R')
        view_connection_data = QAction('Connection &Data', self.bar)
        view_connection_data.setShortcut('Ctrl+D')

        # Tshoot options
        tshoot_errors = QAction('Tshoot &Errors', self.bar)
        tshoot_errors.setShortcut('Ctrl+E')
        tshoot_pcap = QAction('Tshoot &with Pcaps', self.bar)
        tshoot_pcap.setShortcut('Ctrl+W')

        # Help options
        help_support = QAction('Get S&upport', self.bar)
        help_support.setShortcut('Ctrl+U')
        help_about = QAction('A&bout', self.bar)
        help_about.setShortcut('Ctrl+B')

        self.file_menu.addAction(file_open)
        self.file_menu.addAction(file_save)
        self.file_menu.addAction(file_quit)
        self.edit_menu.addAction(edit_preferences)
        self.view_menu.addAction(view_interfaces)
        self.view_menu.addAction(view_routing)
        self.view_menu.addAction(view_connection_data)
        self.tshoot_menu.addAction(tshoot_errors)
        self.tshoot_menu.addAction(tshoot_pcap)
        self.help_menu.addAction(help_support)
        self.help_menu.addAction(help_about)

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

    @staticmethod
    def file_open_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        # Might use this to open a saved vpn config
        show_feature_in_development_dialog()
        pass

    @staticmethod
    def file_save_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        # Might use this to save a vpn config
        show_feature_in_development_dialog()
        pass

    @staticmethod
    def file_quit_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        exit()

    def edit_prefs_action(self):
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
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
    def view_interfaces_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        # If linux/macos > ifconfig
        # If Windows > ipconfig /all
        show_feature_in_development_dialog()
        pass

    @staticmethod
    def view_routing_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        # If linux/macos > netstat -rn
        # If Windows > route print
        show_feature_in_development_dialog()
        pass

    @staticmethod
    def view_data_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        show_feature_in_development_dialog()
        pass

    @staticmethod
    def tshoot_error_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        # In Windows, use powershell: get-eventlog
        show_feature_in_development_dialog()
        pass

    @staticmethod
    def tshoot_pcap_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        show_feature_in_development_dialog()
        pass

    @staticmethod
    def help_support_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        # Redirect to Meraki's support website
        webbrowser.open('https://meraki.cisco.com/support')

    @staticmethod
    def help_about_action():
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        about_popup = QDialog()
        about_popup.setWindowTitle("Meraki Client VPN: About")
        about_program = QLabel()
        about_program.setText("<h1>Meraki VPN Client 0.5.1</h1>\n"
                              "Developed by Ross Jacobs<br><br><br>"
                              "This project is licensed with the "
                              "Apache License, which can be viewed below:")
        license_text = open("LICENSE", 'r').read()
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
