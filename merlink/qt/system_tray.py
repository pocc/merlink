"""System Tray elements."""
import webbrowser
import sys

from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QFont

from merlink.os_utils import open_vpnsettings
from merlink.os_utils import pyinstaller_path


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