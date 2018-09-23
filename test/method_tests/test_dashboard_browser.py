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
from test.credentials import emails, passwords


class TestLogins(unittest.TestCase):
    """Test the dashboard browser class."""

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

    def test_login_success_all_account_types(self):
        """Cycle through access types
        Emails list has these emails: [
            # test for all access
            # test for full org + 1 network access in different org
            # test for full network access in multiple orgs
            # test for read only access in one network in one org
            # test for monitor only access in one network in one org
            # test for guest ambassador access in one network in one org
            # NOT BEING TESTED: TFA (why there's a -1 for enumerate.
        ]
        """
        for i in range(len(emails)-1):
            self.assertEqual(self.browser.login(emails[i], passwords[i]),
                             'auth_success')
            self.tearDown()
            self.setUp()

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
