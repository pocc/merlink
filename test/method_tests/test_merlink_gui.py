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
from merlink.merlink_gui import LoginDialog, MainWindow


class TestLoginDialog(unittest.TestCase):
    """Test the dashboard browser class."""

    @staticmethod
    def set_up():
        """Set up the test."""
        pass

    @staticmethod
    def test_a_fn():
        """Test these functions... eventually.
        show_login
        get_login_info
        check_login_attempt
        tfa_dialog_setup
        tfa_verify
        """
        LoginDialog()


class TestMerlinkWindow(unittest.TestCase):
    """Test the dashboard browser class."""

    @staticmethod
    def set_up():
        """Set up the test."""
        pass

    @staticmethod
    def test_a_fn():
        """Test these functions... eventually.
        attempt_login
        init_ui
        change_organization
        change_network
        refresh_network_dropdown
        setup_vpn
        get_vpn_data
        get_vpn_options
        communicate_vpn_success
        communicate_vpn_failure
        """
        MainWindow()


if __name__ == '__main__':
    unittest.main()
