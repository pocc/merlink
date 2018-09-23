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
"""Test dashboard browser class."""
import unittest
from merlink.browsers.pages import mx, mr, ms


class TestPageRoutes(unittest.TestCase):
    """Test the dashboard browser class."""

    @staticmethod
    def set_up():
        """Set up the test."""
        pass

    @staticmethod
    def test_a_fn():
        """Test these functions... eventually.
        'mr_get_group_policies_by_device_type_enabled',
        'mr_get_ssids',
        'ms_get_management_vlan',
        'ms_get_rstp_enabled',
        'mx_get_active_directory_enabled',
        'mx_get_amp_enabled',
        'mx_get_client_auth_type',
        'mx_get_client_vpn_dns_mode',
        'mx_get_client_vpn_nameservers',
        'mx_get_client_vpn_secret',
        'mx_get_client_vpn_subnet',
        'mx_get_client_vpn_wins_enabled',
        'mx_get_ids_mode',
        'mx_get_ids_ruleset',
        'mx_get_primary_uplink',
        'mx_get_sentry_vpn_enabled',
        """


if __name__ == '__main__':
    unittest.main()
