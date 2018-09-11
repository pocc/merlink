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

"""This should run after a connection has resulted in failure."""

from sys import platform
from os import system

from src.gui.modal_dialogs import show_error_dialog


class TroubleshootVpn:
    """Checks for things that could prevent the VPN connection.

    This class will perform the (currently 6) tests to see what might be
    causing VPN issues. Once all tests have been done, all results can be
    retrieved with the get_test_results() method.

    Attributes:
        pagetext (dict): Contain these input variables:
            * HTML text of appliance status page
            * HTML text of client vpn page
        addr (dict): Contain these input variables:
            * ddns address of the current firewall
            * ip address of the current firewall
        test_results (list(bool)): A bool list of tests passed/failed
    """

    def __init__(self, fw_status_text, client_vpn_text, ddns, firewall_ip):
        super(TroubleshootVpn, self).__init__()
        # Set required variables from merlink_gui
        self.pagetext = {
            'fw_status': fw_status_text,
            'client_vpn': client_vpn_text,
        }
        self.addr = {
            'ip': firewall_ip,
            'ddns': ddns,
        }

        # False for failed, True for passed
        self.test_results = [True] * 6
        self.run_tests()

    def run_tests(self):
        """Iterate through all of the tests."""
        self.test0_is_mx_online()
        self.test1_is_fw_reachable()
        self.test2_is_user_behind_fw()
        self.test3_is_client_vpn_enabled()
        self.test4_is_auth_type_meraki()
        self.test5_incompatible_port_forwards()

    def test0_is_mx_online(self):
        """Tests whether there is an MX in the appliance network.

        # No 'status#' in HTML means there is no firewall in that network

        Raises:
            In progress...
        """
        is_online_status_code = int(
            self.pagetext['fw_status'][
                self.pagetext['fw_status'].find("status#") + 9])
        # Default for test_results is true, so else isn't necessary
        # 0 is online, 2 is unreachable. There are probably other statuses
        if is_online_status_code != 0:
            self.test_results[0] = False

        """ try except clause will be more useful if we know exactly which error
        it causes so we can except it
        try:
        except:
            # No 'status#' in HTML means there is no firewall in that network
            error_dialog("There is no device in this network!")
        """

    def test1_is_fw_reachable(self):
        """Verify whether firewall is reachable by pinging 4 times

        If at least one ping that made it, mark this test as successful.
        """

        if platform == 'win32':  # Identifies any form of Windows
            # ping 4 times every 1000ms
            ping_string = "ping " + self.addr['ddns']
        else:  # *nix of some kind
            # ping 4 times every 200ms
            ping_string = "ping -c 5 -i 0.2 " + self.addr['ddns']
        ping_response = system(ping_string)
        # Ping responses other than 0 mean failure. Error codes are OS-dependent
        if ping_response != 0:
            self.test_results[1] = False
            # Failure error dialog and then return
            show_error_dialog("Cannot connect to device!")

    def test2_is_user_behind_fw(self):
        """Tests whether the user is behind the firewall.

        If the user is behind their firewall, they will not be able to connect
        (and a VPN connection would be pointless.) request_ip is the IP is
        the source public IP that the user is connecting with.
        """

        ip_start = self.pagetext['fw_status'].find("\"request_ip\":") + 14
        # Get the position of the IP end quote
        ip_end = self.pagetext['fw_status'][ip_start:].find('\"') + ip_start
        src_public_ip = self.pagetext['fw_status'][ip_start:ip_end]
        # If public IP address of client == MX IP
        # Then the user is behind their firewall and client vpn won't work
        if src_public_ip == self.addr['ip']:
            self.test_results[2] = False

    def test3_is_client_vpn_enabled(self):
        """Tests whether client VPN is enabled.

        If client VPN is not enabled, the firewall will not respond to
        client VPN requests."""
        if self.pagetext['client_vpn'][self.pagetext['client_vpn'].find(
                ",\"client_vpn_enabled\"") + 22] != 't':
            self.test_results[3] = False

    def test4_is_auth_type_meraki(self):
        """Is the authentication type is Meraki Auth?

        For the time being, flag use of RADIUS or Active Directory
        as an error as those auth types aren't being tested against.

        When an auth type is selected, we get one of these
        in the client VPN HTML depending on user's auth choice:

        Meraki cloud</option></select>
        Active Directory</option></select>
        RADIUS</option></select>
        """
        # String find returns -1 if the string isn't found
        meraki_select_type1 = self.pagetext['client_vpn'].find(
            'Meraki cloud</option></select>')
        meraki_select_type2 = self.pagetext['client_vpn'].find(
            '<option value="meraki" selected="selected">')
        if meraki_select_type1 == -1 and meraki_select_type2 == -1:
            self.test_results[4] = False
            show_error_dialog(
                "ERROR: Please select Meraki cloud authentication")

    def test5_incompatible_port_forwards(self):
        """Test for port forwards that break an IPSEC VPN.

        An IPSEC connection uses UDP port 500 and UDP port 4500 if there is NAT.
        If the following text exists, they're port forwarding ports 500 or 4500:
        "public_port":"500"
        "public_port":"4500"
        """
        # -1 is returned by string find if a match is not found
        is_forwarding_500 = self.pagetext['client_vpn'].find(
            '"public_port":"500"') != -1
        is_forwarding_4500 = self.pagetext['client_vpn'].find(
            '"public_port":"4500"') != -1
        if is_forwarding_500:
            show_error_dialog("ERROR: You are forwarding port 500!")
            self.test_results[5] = False

        if is_forwarding_4500:
            show_error_dialog("ERROR: You are forwarding port 4500!")
            self.test_results[5] = False

        """
        # *** TEST 6 *** : CURRENTLY ON HOLD
        # Is user authorized for Client VPN?
        # By definition, if you can log in as an administrator,
        # you have an admin user in the Client VPN users page

        # This is the only test which requires us to scrape data from a table.
        # Tables in dashboard use javascript,
        # So we need to scrape differently.
        # https://stackoverflow.com/questions/8049520/
        
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        # Last I checked this was necessary.
        driver = webdriver.Chrome('/usr/bin/google-chrome',
                                  chrome_options=options)
        driver.get(self.client_vpn_url)
        print(driver.find_elements_by_css_selector('td.ft.notranslate.email'))
        """

    def get_test_results(self):
        """Returns the test results after tests have been run."""
        return self.test_results
