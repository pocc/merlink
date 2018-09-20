# -*- coding: utf-8 -*-

"""Test dashboard browser class."""
import unittest
from merlink.browsers.dashboard import DashboardBrowser


class TestDashboardBrowser(unittest.TestCase):
    """Test the dashboard browser class."""

    @staticmethod
    def set_up():
        """Set up the test."""
        pass

    @staticmethod
    def test_a_fn():
        """Test these functions... eventually.
        """
        browser = DashboardBrowser()
        browser.org_data_setup()


if __name__ == '__main__':
    unittest.main()
