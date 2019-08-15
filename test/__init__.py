# -*- coding: utf-8 -*-
"""Files to test MerLink.

There are 8 components of Merlink functionality:
0. CLI (+integration tests)
1. GUI (+integration tests)
2. Client VPN additions to Soup Browser
3. Dashboard VPN additions to Soup Browser
4. Test page routes
5. VPN connection
6. Utils scattered around the program
7. Mechanical Turk: Things that must be tested manually for the time being.
"""

import unittest

from test.method_tests.test_client_vpn_browser import TestClientVpnBrowser
from test.method_tests.test_dashboard_browser import TestLogins
from test.method_tests.test_merlink_cli import TestMerlinkCli
from test.method_tests.test_merlink_gui import TestMerlinkWindow
from test.method_tests.test_page_routes import TestPageRoutes
from test.method_tests.test_vpn_connection import TestVpnConnection

"""
fast = unittest.TestSuite()
fast.addTests([
    TestClientVpnBrowser,
    TestMerlinkCli,
    TestMerlinkWindow,
    TestPageRoutes,
    TestVpnConnection
])

slow = unittest.TestSuite()
slow.addTests(TestLogins)

alltests = unittest.TestSuite([fast, slow])
"""