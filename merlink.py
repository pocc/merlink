#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls
# Build this with './venv/bin/python3 setup.py build' from project root

import sys
from PyQt5.QtWidgets import QApplication
from src.modules.merlink_gui import MainWindow
from src.modules.merlink_cli import MainCli


def main():  # Syntax per PyQt recommendations: http://pyqt.sourceforge.net/Docs/PyQt5/gotchas.html
    # If there is one argument, start GUI
    # Otherwise, start CLI
    if len(sys.argv) == 1:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # We want to be able to be connected with VPN with systray icon
        merlink_gui = MainWindow()
        merlink_gui.show()

        sys.exit(app.exec_())

    else:
        merlink_cli = MainCli()


if __name__ == '__main__':
    main()
