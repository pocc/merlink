# -*- coding: utf-8 -*-
"""Files to test MerLink.

There are 7 components of Merlink functionality:
0. CLI (+integration tests)
1. GUI (+integration tests)
2. Client VPN additions to Soup Browser
3. Dashboard VPN additions to Soup Browser
4. Test page routes
5. VPN connection
6. Utils scattered around the program
"""
import unittest

from .test_client_vpn_browser import TestClientVpnBrowser
from .test_dashboard_browser import TestDashboardBrowser
from .test_merlink_cli import TestMerlinkCli
from .test_merlink_gui import TestMerlinkWindow, TestLoginDialog
from .test_page_routes import TestPageRoutes
from .test_vpn_connection import TestVpnConnection


TestClientVpnBrowser()
TestDashboardBrowser()
TestMerlinkCli()
TestMerlinkWindow()
TestPageRoutes()
TestVpnConnection()