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

from merlink.browsers.dashboard import DashboardBrowser
from merlink.browsers.pages.page_utils import get_input_var_value
from test.credentials import emails, passwords


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
            # NOT BEING TESTED: TFA
        ]
    """

    def setUp(self):
        """Set up the test."""
        self.browser = DashboardBrowser()

    def test_login_sms(self):
        """Test for a user known to be using tfa auth"""
        self.assertEqual(self.browser.login(emails[6], passwords[6]),
                         'sms_auth')

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

        * Navigate to organization settings in primary org
        * Navigate to network settings in other org
        """
        self.browser.login(emails[1], passwords[1])
        # Force first org to be one where user has org access
        if not self.browser.orgs_dict['org_admin_type']:  # If no org access
            # Set org id to the org with full access
            self.toggle_orgs()

        # Check org access in the first org and check network access in 2nd.
        self.check_org_access()
        self.toggle_orgs()
        self.check_network_access()

    def test_login_2networks_diff_orgs(self):
        self.browser.login(emails[2], passwords[2])
        self.check_network_access()
        self.toggle_orgs()
        self.check_network_access()

    def test_login_1network_read_only(self):
        self.browser.login(emails[3], passwords[3])
        self.check_network_access()

    def test_login_1network_monitor_only(self):
        self.browser.login(emails[4], passwords[4])
        self.check_network_access()

    def test_login_1network_guest_ambassador(self):
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

    def check_org_access(self):
        """Verify org access by scraping the org name out of settings."""
        # Print name that should only be visible on Organization > Settings
        self.browser.open_route('/organization/edit')
        with open('org.html', 'w') as file:
            file.write(str(self.browser.get_page()))
            file.close()
        print('Org name:', get_input_var_value(self.browser.get_page(),
                                               'organization_name'))

    def check_network_access(self):
        """Verify network access by scraping its name from network settings.

        In combined networks, this call redirects to /configure/general.
        As the page content is the same, allow the redirect.
        """
        self.browser.open_route('/configure/system_settings', redirect_ok=True)
        # Print name that should only be visible on Network-wide > General
        print('Network name:', get_input_var_value(self.browser.get_page(),
                                                   'network_name'))

    def tearDown(self):
        """Logout of browser and close it."""
        self.browser.logout()
        self.browser.browser.close()


if __name__ == '__main__':
    unittest.main()

"""Test these functions... eventually.
'combined_network_redirect', 
'get_active_network_name', 
'get_active_org_name',
'get_network_names',
'get_org_names',
'handle_redirects',
'login', 
'logout', 
'open_route', 
'org_data_setup', 
'scrape_json', 
'set_network_id', 
'set_network_name', 
'set_org_id', 
'set_org_name', 
'tfa_submit_info', 
'url'
"""
