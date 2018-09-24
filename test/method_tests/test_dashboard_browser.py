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
"""Test dashboard browser class.

A credentials file with username + password must be supplied for this to work.
('credentials*' is excluded in .gitignore)
"""
import unittest
import requests
import re
import pyotp

from merlink.browsers.dashboard import DashboardBrowser
from merlink.browsers.pages.page_utils import get_input_var_value
from merlink.browsers.pages.page_hunters import get_pagetext_mkiconf
from test.credentials import emails, passwords, totp_base32_secret


class TestLogins(unittest.TestCase):
    """Test the dashboard browser class.

    Cycle through access types
        Emails list has these emails: [
            # test for all access
            # test for full org + 1 network access in different org
            # test for full network access in multiple orgs
            # test for read only access in one network in one org
            # test for monitor only access in one network in one org
            # test for guest ambassador access in one network in one org
            # test for tfa network admin access in one network in one org
        ]
    """

    def setUp(self):
        """Set up the test."""
        self.browser = DashboardBrowser()

    def test_login_sms_redirect(self):
        """Test that a tfa user is redirected to the tfa page."""
        self.assertEqual(self.browser.login(emails[6], passwords[6]),
                         'sms_auth')

    def test_login_tfa_fail(self):
        """Verify that bad TFA code returns expected ValueError exception."""
        self.browser.login(emails[6], passwords[6], tfa_code='000000')
        with self.assertRaises(ValueError):
            self.check_network_access()

    def test_login_tfa(self):
        """Verify that tfa works with python authenticator `pyotp`."""
        totp = pyotp.TOTP(totp_base32_secret)
        self.browser.login(emails[6], passwords[6], tfa_code=totp.now())
        self.check_network_access()

    def test_login_failure(self):
        """Test whether sending a bad password will result in an auth error."""
        self.assertEqual(self.browser.login(emails[6], 'badpassword'),
                         'auth_error')

    def test_login_success(self):
        """Test whether login works with a user with known good email/pass."""
        self.assertEqual(self.browser.login(emails[0], passwords[0]),
                         'auth_success')

    def test_login_multiorg(self):
        """Test whether a user with 2 orgs can access everything they should.

        * Checks org access in both orgs.
        """
        self.browser.login(emails[0], passwords[0])
        self.check_org_access()
        self.toggle_orgs()
        self.check_org_access()

    def test_login_1org_1network(self):
        """Test access for user with 1 org and 1 network in another org

        * Navigate to organization settings in org with full access
        * Navigate to network settings in other org where user does not have
          org access
        """
        self.browser.login(emails[1], passwords[1])
        # Force first org to be one where user has org access
        this_org = self.browser.active_org_id
        if not self.browser.orgs_dict[this_org]['org_admin_type']:
            # Set org id to the org with full access
            self.toggle_orgs()

        # Check org access in the first org and check network access in 2nd.
        self.check_org_access()
        self.toggle_orgs()
        self.check_network_access()

    def test_login_2networks_diff_orgs(self):
        """Test access for admin with network access in 2 diff orgs."""
        self.browser.login(emails[2], passwords[2])
        self.check_network_access()
        self.toggle_orgs()
        self.check_network_access()

    def test_login_1network_read_only(self):
        """Test access for network read-only admin."""
        self.browser.login(emails[3], passwords[3])
        self.check_network_access()

    def test_login_1network_monitor_only(self):
        """Test access for network monitors in 1 network in 1 org.

        Network monitors only have access to /usage/list, /new_reports
        """
        self.browser.login(emails[4], passwords[4])
        self.check_network_access(route='/new_reports')

    def test_login_1network_guest_ambassador(self):
        """Test access for network amabassadors in 1 network in 1 org.

        Guest ambassadors only have access to /configure/guests
        """
        self.browser.login(emails[5], passwords[5])
        self.check_network_access()

    def get_other_org_id(self):
        """For tests that involve multiple orgs, get the org not active now."""
        return [item for item in list(self.browser.orgs_dict.keys())
                if item not in [self.browser.active_org_id]][0]

    def toggle_orgs(self):
        """Set the org id to that of the other org.

        In many of these tests, there are admins with access to 2 orgs.
        This function allows us to quickly toggle between the two
        """
        self.browser.set_org_id(self.get_other_org_id())
        print('Switching to org:\t', self.browser.get_active_org_name())

    def check_org_access(self):
        """Verify org access by scraping the org name out of settings."""
        # Print name that should only be visible on Organization > Settings
        self.browser.open_route('/organization/edit')
        print('Testing org access...\nOpened org:\t\t\t', get_input_var_value(
            self.browser.get_page(), 'organization_name'))

    def check_network_access(self, route='/configure/guests'):
        """Verify network access by scraping its name from network settings.

        Using /configure/guests as it should be accessible for all user types.
        MkiConf vars will be scrapeable even if this page lacks content.
        """
        network_eid = self.browser.active_network_id
        self.browser.open_route(route, network_eid=network_eid)
        mkiconf_dict = get_pagetext_mkiconf(self.browser.get_page().text)
        print('Testing network access...\nOpened network:\t\t',
              mkiconf_dict['network_name'])

    def tearDown(self):
        """Logout of browser and close it."""
        self.browser.logout()
        self.browser.browser.close()


if __name__ == '__main__':
    unittest.main()

"""Test these functions... eventually.
'get_active_network_name', 
'get_active_org_name',
'get_network_names',
'get_org_names',
'set_network_id', 
'set_network_name', 
'set_org_id', 
'set_org_name', 

'handle_redirects',
'combined_network_redirect', 
'open_route', 
'org_data_setup', 
'scrape_json',  
"""
