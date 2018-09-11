# -*- coding: utf-8 -*-

"""Test dashboard browser class."""
import unittest
from src.dashboard_browser.dashboard_browser import DashboardBrowser


class TestDashboardBrowser(unittest.TestCase):
    """Test the dashboard browser class."""

    @staticmethod
    def set_up():
        """Set up the test."""
        pass

    @staticmethod
    def test_a_fn():
        """Test these functions... eventually.

        DataScraper.bypass_org_choose_page()
        DataScraper.filter_org_data()
        DataScraper.get_active_network_url()
        DataScraper.get_active_org_index()
        DataScraper.get_active_org_name()
        DataScraper.get_active_org_networks()
        DataScraper.get_browser()
        DataScraper.get_mkiconf_vars()
        DataScraper.get_org_names()
        DataScraper.get_url()
        DataScraper.scrape_administered_orgs()
        DataScraper.scrape_ddns_and_ip()
        DataScraper.scrape_network_vars()
        DataScraper.scrape_psk()
        DataScraper.set_active_org_index()
        """
        browser = DashboardBrowser()
        browser.org_data_setup()


if __name__ == '__main__':
    unittest.main()
