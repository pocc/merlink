#!/usr/bin/python3
# This should run after a connection has resulted in failure

# Library imports
from sys import platform
from os import system

# Local imports
from src.gui.modal_dialogs import show_error_dialog, show_feature_in_development_dialog


class TroubleshootVpnFailure:
    def __init__(self, fw_status_text, client_vpn_text, ddns_address, firewall_ip):
        super(TroubleshootVpnFailure, self).__init__()

        # Set required variables from merlink_gui
        self.fw_status_text = fw_status_text
        self.client_vpn_text = client_vpn_text
        self.ddns_address = ddns_address
        self.firewall_ip = firewall_ip

        """
        This method will check all of these values and show which are invalid
        User should not be able to connect if there are any tests that fail (i.e grayed out button)
        Each test should be clickable so that the user can find out more information
        """
        self.has_passed_validation = [True] * 6  # False for failed, True for passed
        self.run_tests()

    def run_tests(self):
        # Go through tests and then show results
        self.test0_is_mx_online()
        self.test1_is_fw_reachable()
        self.test2_is_user_behind_fw()
        self.test3_is_client_vpn_enabled()
        self.test4_is_auth_type_meraki()
        self.test5_incompatible_port_forwards()

        self.show_results()

    def test0_is_mx_online(self):
        # Tests whether there is an MX in the appliance network
        is_online_status_code = int(self.fw_status_text[self.fw_status_text.find("status#") + 9])
        # Default for has_passed_validation is true, so else isn't necessary
        if is_online_status_code != 0:  # 0 is online, 2 is unreachable. There are probably other statuses
            self.has_passed_validation[0] = False

        """ try except clause will be more useful if we know exactly which error it causes so we can except it
        try:
        except:
            # No 'status#' in HTML means there is no firewall in that network
            error_dialog("There is no device in this network!")
        """

    def test1_is_fw_reachable(self):
        # Verify
        # Ping 4 times
        if platform == 'win32':  # Identifies any form of Windows
            ping_string = "ping " + self.ddns_address  # ping 4 times every 1000ms
        else:  # *nix of some kind
            ping_string = "ping -c 5 -i 0.2 " + self.ddns_address  # ping 4 times every 200ms
        ping_response = system(ping_string)
        if ping_response != 0:  # Ping responses other than 0 mean failure. Error codes are OS-dependent
            self.has_passed_validation[1] = False
            # Failure error dialog and then return
            show_error_dialog("Cannot connect to device!")

    def test2_is_user_behind_fw(self):
        # *** TEST 2 ***
        # Is the user behind the firewall?
        # This IP is the source public IP that the user is connecting with
        ip_start = self.fw_status_text.find("\"request_ip\":") + 14  # Start of IP position
        ip_end = self.fw_status_text[ip_start:].find('\"') + ip_start  # Get the position of the IP end quote
        src_public_ip = self.fw_status_text[ip_start:ip_end]
        # If public IP address of client == MX IP
        # Then the user is behind their firewall and client vpn won't work
        if src_public_ip == self.firewall_ip:
            self.has_passed_validation[2] = False

        """try except clause will be more useful if we know what type of error to except    
        try:
        except:
        #    error_dialog("Exception during source public IP == MX IP test")
        """

    def test3_is_client_vpn_enabled(self):
        # *** TEST 3 ***
        # Is Client VPN enabled?
        if self.client_vpn_text[self.client_vpn_text.find(",\"client_vpn_enabled\"") + 22] != 't':
            self.has_passed_validation[3] = False

    def test4_is_auth_type_meraki(self):
        # *** TEST 4 ***
        # Authentication type is Meraki Auth?
        # User fixes (for now)
        """ When an auth type is selected, we get one of these in the client VPN HTML depending on user's auth choice:
        Meraki cloud</option></select>
        Active Directory</option></select>
        RADIUS</option></select>
        """
        # String find returns -1 if the string isn't found
        meraki_select_type1 = self.client_vpn_text.find('Meraki cloud</option></select>')
        meraki_select_type2 = self.client_vpn_text.find('<option value="meraki" selected="selected">')
        if meraki_select_type1 == -1 and meraki_select_type2 == -1:
            self.has_passed_validation[4] = False
            show_error_dialog("ERROR: Please select Meraki cloud authentication")

    def test5_incompatible_port_forwards(self):
        # *** TEST 5 ***
        """
        If the following text exists, they're port forwarding ports 500 or 4500:
        "public_port":"500"
        "public_port":"4500"
        """
        # -1 is returned by string find if a match is not found
        is_forwarding_500 = self.client_vpn_text.find('"public_port":"500"') != -1
        is_forwarding_4500 = self.client_vpn_text.find('"public_port":"4500"') != -1
        if is_forwarding_500:
            show_error_dialog("ERROR: You are forwarding port 500!")
            self.has_passed_validation[5] = False

        if is_forwarding_4500:
            show_error_dialog("ERROR: You are forwarding port 4500!")
            self.has_passed_validation[5] = False

        # *** TEST 6 *** : CURRENTLY ON HOLD
        # Is user authorized for Client VPN?
        # By definition, if you can log in as a user, you have a user in the Client VPN users page

        # This is the only test which requires us to scrape data from a table. Tables in dashboard use javascript,
        # So we need to scrape differently.
        # https://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python
        """ from selenium import webdriver
         from selenium.webdriver.chrome.options import Options
         options = Options()
         options.add_argument('--headless')
         # options.add_argument('--disable-gpu')  # Last I checked this was necessary.
         driver = webdriver.Chrome('/usr/bin/google-chrome', chrome_options=options)
         driver.get(self.client_vpn_url)
         print(driver.find_elements_by_css_selector('td.ft.notranslate.email'))
        """

    def show_results(self):
        if not self.has_passed_validation[3]:
            show_error_dialog('Client VPN is not enabled in Dashboard for this network.')

    def get_test_results(self):
        return self.has_passed_validation
