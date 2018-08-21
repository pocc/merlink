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

"""This class manages the system tray icon."""
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QFont
import webbrowser

from src.modules.pyinstaller_path_helper import resource_path


class SystrayIcon:
    # Taking in 'app', which is the MainWindow object
    def __init__(self, app):
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        # Init QSystemTrayIcon
        # Set the Window and Tray Icons
        self.app = app
        self.app.setWindowIcon(QIcon(resource_path('src/media/miles.ico')))
        self.tray_icon = QSystemTrayIcon(app)
        self.tray_icon.setIcon(QIcon(resource_path('src/media/miles.ico')))
        if app.is_vpn_connected():
            connection_status = 'VPN connected'
        else:
            connection_status = 'VPN disconnected'
        self.tray_icon.setToolTip("Merlink - " + connection_status)
    
        # TODO this should be a drop down of saved connections
        connect_action = QAction("Connect to ...", app)
        # These 3 lines are to make "Connect to ..." bold
        f = QFont()
        f.setBold(True)
        connect_action.setFont(f)
    
        disconnect_action = QAction("Disconnect", app)
        show_action = QAction("Show", app)
        quit_action = QAction("Exit", app)
        hide_action = QAction("Hide", app)
        # Allow this if we're not connected
        connect_action.triggered.connect(app.connect_vpn)
        disconnect_action.triggered.connect(app.disconnect)
        show_action.triggered.connect(app.show)
        hide_action.triggered.connect(app.hide)
        quit_action.triggered.connect(exit)
    
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
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.app.show()  # So it will show up in taskbar
            self.app.raise_()  # for macOS
            self.app.activateWindow()  # for Windows

        elif reason == QSystemTrayIcon.MiddleClick:
            # Go to Security Appliance that we've connected to
            # TODO This is going to need more legwork as we need to pass the
            # TODO cookie when we open the browser
            webbrowser.open("https://meraki.cisco.com/")

        # Override closeEvent, to intercept the window closing event
        # The window will be closed if there is no check mark in the check box

    def application_minimized(self):
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        self.tray_icon.showMessage(
            "Merlink",
            "Merlink is now minimized",
            QSystemTrayIcon.Information,
            1000
        )

    def set_vpn_failure(self):
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        self.app.setIcon(QIcon(resource_path('src/media/unmiles.ico')))

    # There's no such thing as "minimize to system tray".
    # What we're doing is hiding the window and
    # then adding an icon to the system tray
    def set_vpn_success(self):
        """Short desc

        Extended desc

        Args:
        Returns:
        Returns:
        """

        self.tray_icon.setIcon(QIcon(resource_path(
            'src/media/connected_miles.ico')))
        # If user wants to know more about connection,
        # they can click on message and be redirected
        self.tray_icon.messageClicked.connect(self.app.open_vpn_settings)
        # Show the user the message so they know where the program went
        self.tray_icon.showMessage(
            "Merlink",
            "Succesfully connected!",
            QSystemTrayIcon.Information,
            2000
        )
