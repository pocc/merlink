#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls
# Build this with './venv/bin/python3 setup.py build' from project root

import sys
from PyQt5.QtWidgets import QApplication
from src.modules.main_window import MainWindow


def main():  # Syntax per PyQt recommendations: http://pyqt.sourceforge.net/Docs/PyQt5/gotchas.html
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # We want to be able to be connected with VPN with systray icon
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
