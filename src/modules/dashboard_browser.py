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

"""API to interact with the Meraki Dashboard using the requests module."""
import re
import json

import requests
import mechanicalsoup
import bs4


class DataScraper:
    """API to interact with the Meraki Dashboard using the requests module.

    Attributes:
        username (string): User-entered username, used to login
        password (string): User-entered password, used to login
        browser (MechanicalSoup): Main browser object to send data to dashboard

    TODO: Convert the other attributes to a dict
    """
    def __init__(self):
        super(DataScraper, self).__init__()

        # Setup browser for use by other components
        self.username = ''
        self.password = ''
        # Instantiate browser
        self.browser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},  # Use the lxml HTML parser
            raise_on_404=True,
            # User Agent String is for the Nintendo Switch because why not
            user_agent='Mozilla/5.0 (Nintendo Switch; ShareApplet) '
                       'AppleWebKit/601.6 (KHTML, like Gecko) '
                       'NF/4.0.0.5.9 NintendoBrowser/5.1.0.13341',
        )
        # Set tfa_success to false
        self.tfa_success = False

        # By default, you have access to 0 orgs
        self.org_qty = 0
        # Initialize organization dictionary {Name: Link} and
        # list for easier access. org_list is org_links.keys()
        self.org_links = {}
        self.org_list = []
        self.network_list = []
        self.base_url_list = []
        self.current_org = 'Org Placeholder'  # Org name placeholder
        self.current_org_index = 0  # Default to first organization
        self.network_admin_only = False  # Most admins are org admins

        # VPN VARS: Powershell Variables set to defaults
        self.current_ddns = '-'  # set to default hyphen char as a failsafe
        # Expected behavior is to have full-tunnel by default
        self.split_tunnel = False
        self.remember_credential = False
        # If it's set to '', then powershell will skip reading that parameter.
        self.DnsSuffix = '-'
        # Powershell default for not disconnecting until after x seconds
        self.IdleDisconnectSeconds = 0
        self.UseWinlogonCredential = False
        self.is_connected = False
        self.username = ''
        self.password = ''

        self.current_network = ''
        self.client_vpn_url = ''
        self.client_vpn_text = ''
        self.client_vpn_soup = ''
        self.psk = ''

        self.fw_status_text = ''
        self.current_primary_ip = ''

    def get_url(self):
        """Get the current URL"""
        print("browser url in get_url" + str(self.browser.get_url()))
        return self.browser.get_url()

    def get_tfa_success(self):
        """Get the TFA success bool"""
        return self.tfa_success

    # Return browser with any username, password, and cookies with it
    def get_browser(self):
        """Get the MechanicalSoup object with associated login cookies."""
        return self.browser

    def get_networks_by_org_index(self, org_index):
        """Returns the array of networks from an org by its index."""
        print("Network list: " + str(self.network_list))
        return self.network_list[org_index]

    def attempt_login(self, username, password):
        """Verifies whether credentials are valid

        Uses a MechanicalSoup object to send and submit username/password.
        The resultant URL is different for each au
        Args:
        Returns:th eventuality and
        is used to identify each.

        Args:
            username (string): The username provided by the user
            password (string): The password provided by the user

        Returns:
            (string): One of ('auth_error', 'sms_auth', 'auth_success')
              indicating the next login step.
        """

        # Set up required vars
        self.username = username
        self.password = password

        # Navigate to login page
        self.browser.open('https://account.meraki.com/login/dashboard_login')
        form = self.browser.select_form()
        self.browser["email"] = self.username
        self.browser["password"] = self.password
        form.choose_submit('commit')  # Click login button
        self.browser.submit_selected()  # response should be '<Response [200]>'
        print("browser url in attempt login " + str(self.browser.get_url()))

        # After setup, verify whether user authenticates correctly
        result_url = self.browser.get_url()
        # URL contains /login/login if login failed

        if '/login/login' in result_url:
            return 'auth_error'
        # Two-Factor redirect: https://account.meraki.com/login/sms_auth?go=%2F
        elif 'sms_auth' in result_url:
            return 'sms_auth'
        else:
            return 'auth_success'

    def tfa_submit_info(self, tfa_code):
        """Attempt login with the provided TFA code.

        Args:
            tfa_code (string): The user-entered TFA string (should consist of
            6 digits)
        """

        form = self.browser.select_form()
        print(self.browser.get_url())
        self.browser['code'] = tfa_code
        form.choose_submit('commit')  # Click 'Verify' button
        self.browser.submit_selected()

        current_page = self.browser.get_current_page().text
        # Will return -1 if it is not found
        if current_page.find("Invalid verification code") == -1:
            print("TFA Success")
            return True
        else:
            print("TFA Failure")

    def scrape_initial_org_info(self):
        """Scrape the initial org info so that we have somthing to show user.

        This function will get the organizations and then save them as a dict
        of names and links. Gestalt, this function gets info so there is
        something to show the user as part of the initial ui

        NOTE: Don't set data for network-only admins as they don't have
        org-access. Network-only admin data is added in get_networks().
        """
        print("In fn [scrape_orgs()]")

        # NOTE: Until you choose an organization, Dashboard will not let you
        # visit pages you should have access to
        page = self.browser.get_current_page()
        # Use pagetext variable so we can have a string we can use slices with
        pagetext = page.text
        # Found in HTML for administrators with access to only 1 org
        # org_str is ONLY found for one org admins
        is_one_org_admin = pagetext.find("org_str")
        org_names = []
        if is_one_org_admin != -1:
            self.org_qty = 1
        else:
            # Get a list of all org links
            org_names = page.findAll('a', href=re.compile(
                '/login/org_choose\?eid=.{6}'))
            # Get the number of orgs
            self.org_qty = len(org_names)

        if self.org_qty == 1:  # org admin with one org
            # This should be present in EVERY dashboard page
            org_name_start = pagetext.find("Mkiconf.org_name") + 20
            org_name_end = org_name_start + pagetext[org_name_start:].find('"')
            one_org_name = pagetext[org_name_start: org_name_end]
            self.org_links[one_org_name] = self.browser.get_url()
            self.org_list.append(one_org_name)
        elif self.org_qty > 1:  # 2+ Orgs admin
            for i in range(self.org_qty):
                org_str = str(org_names[i])
                # 39:-4 = Name, 9:37 = Link
                self.org_links[org_str[39:-4]] = \
                    'https://account.meraki.com' + org_str[9:37]
                self.org_list.append(org_str[39:-4])
                print(org_str[39:-4] + self.org_links[org_str[39:-4]])

        if self.org_qty > 0:
            # Autochoose first organization
            self.current_org = self.org_list[0]
            # Open the first link so the browser object is prepared
            self.browser.open(list(self.org_links.values())[0])
        else:
            self.current_org = 'Org Placeholder'  # Org name placeholder
            self.network_admin_only = True
        # We get org information from administered_orgs for network admins

        for i in range(len(self.org_list)):
            print(self.org_list[i])

    def get_org_list(self):
        """Get this administrator's org list."""
        return self.org_list

    def get_current_org(self):
        """Get the current org."""
        return self.current_org

    def set_current_org(self, current_org_index):
        """Set the current org."""
        self.current_org_index = current_org_index
        self.current_org = self.org_list[current_org_index]

    def get_org_networks(self):
        """Get an org's networks"""
        return self.network_list[self.current_org_index]

    def scrape_org_networks(self):
        """Short desc

        * get_networks should only be called on initial startup or if a
          different organization has been chosen
        * browser should be initialized
        * browser should have clicked on an org in the org selection page so we
          can browse relative paths of an org
        """

        print("In get_networks")

        # If we're dealing with org admins
        if not self.network_admin_only:
            # This method will get the networks by
            # using the administered_orgs json blob
            current_url = self.org_links[self.current_org]
            self.browser.open(current_url)
        current_url = self.browser.get_url()
        # base url is up to '/manage/'
        # boundary between network string and webpage string
        upper_url_index = current_url.find('/manage')
        # boundary between domain string and network string
        lower_url_index = current_url.find('.com/')
        url_domain_part = current_url[:lower_url_index + 4]  # Add 4 for '.com'
        # Add 7 for '/manage'
        url_network_part = current_url[lower_url_index + 4:upper_url_index + 7]
        # For this URL, it doesn't matter which network in an org
        # we get it from because it will be the same
        administered_orgs = url_domain_part + url_network_part \
            + '/organization/administered_orgs'
        self.browser.open(administered_orgs)
        print(administered_orgs)

        cj = self.browser.get_cookiejar()
        print(cj)
        response = requests.get(administered_orgs, cookies=cj)
        administered_orgs_text = response.text

        orgs_dict = json.loads(administered_orgs_text)
        print("orgs_dict " + str(orgs_dict))
        print("current org " + str(self.current_org))

        # For network_only_admins,
        # we first get org info from the administered_orgs page
        if self.network_admin_only:
            self.org_qty = len(orgs_dict.keys())
            for i in range(self.org_qty):
                org_id = list(orgs_dict)[i]
                self.org_list.append(orgs_dict[org_id]['name'])
            # Duplicating this line here as we're ok with network admins
            # running this code multiple times as it's dependent on
            # administerd_orgs json. For org admins, we keep it in
            # scrape_orgs() so it runs once

        print("org_qty " + str(self.org_qty))
        for i in range(self.org_qty):  # For every organization
            # Start out with no network names or network base urls for each org
            self.network_list.append([])
            self.base_url_list.append([])
            network_names = []
            network_base_urls = []

            this_org = list(orgs_dict)[i]  # get this org's id
            # int of num networks
            num_networks = orgs_dict[this_org]['num_networks']
            # Inner dict that contains base64 network name and all network info
            node_groups = orgs_dict[this_org]['node_groups']
            # List of network ids in base64.
            # These networkIds are keys for network data dict that is the value
            network_base64_ids = list(node_groups.keys())
            # For orgs that are not the current org,
            # we will get the number off networks, but get node_groups of {}
            if node_groups == {}:
                num_networks = 0
            for j in range(num_networks):
                node_group_data = node_groups[network_base64_ids[j]]
                if node_group_data['network_type'] == 'wired' and not \
                        node_group_data['is_config_template']:
                    network_names.append(node_group_data['n'])
                    # Reconstructing the base url. 't' is
                    # for network name as it appears in URL
                    network_base_urls.append(
                        url_domain_part + '/' + node_group_data['t'] +
                        '/n/' + node_group_data['eid'] + '/manage')

            # If this is [], fill it with the network names, [] == False
            if not self.network_list[self.current_org_index]:
                print("Adding networks to list")
                self.network_list[self.current_org_index] = network_names
                self.base_url_list[
                    self.current_org_index] = network_base_urls
            print("self.current_org_index " + str(self.current_org_index))
            print(self.network_list[i])

    def scrape_network_vars(self, current_network_index):
        """Scrape primary WAN IP address and the Client VPN PSK

        Args:
            current_network_index (int): The index of the current network in
            the current org.
        """

        self.get_client_vpn_text(current_network_index)

        self.psk = self.client_vpn_soup.find("input", {
            "id": "wired_config_client_vpn_secret", "value": True})['value']
        # Found in html as  ',"client_vpn_enabled":true'
        client_vpn_value_index = self.client_vpn_text.find(
            ",\"client_vpn_enabled\"")

        print(self.client_vpn_text[
              client_vpn_value_index:client_vpn_value_index+27])

        self.scrape_ddns_and_ip(current_network_index)
        # tshoot_vpn_fail_gui() MUST come after scrape_ddns_and_ip()
        # because it needs DDNS/IP address

    def get_client_vpn_text(self, current_network_index):
        """Get client vpn text.

        Args:
            current_network_index (int): The index of the current network in
            the current org.
        """
        self.current_network = str(
            self.network_list[self.current_org_index][current_network_index])
        self.client_vpn_url = \
            self.base_url_list[self.current_org_index][current_network_index] \
            + '/configure/client_vpn_settings'
        print("Client VPN url " + self.client_vpn_url)

        self.client_vpn_text = self.browser.get(self.client_vpn_url).text
        self.client_vpn_soup = bs4.BeautifulSoup(self.client_vpn_text, 'lxml')

    def scrape_ddns_and_ip(self, current_network_index):
        """Scrape the ddns and primary ip address."

        This method gets ddns and ip values for the current network. This
        method should ONLY be called if the user has hit the connect button

        Args:
            current_network_index (int): The index of the current network in
            the current org.
        """
        fw_status_url = \
            self.base_url_list[self.current_org_index][
                current_network_index] + '/nodes/new_wired_status'
        self.fw_status_text = self.browser.get(fw_status_url).text

        # ddns value can be found by searching for '"dynamic_dns_name"'
        ddns_value_start = self.fw_status_text.find("dynamic_dns_name")+19
        ddns_value_end = self.fw_status_text[ddns_value_start:].find('\"') \
            + ddns_value_start
        self.current_ddns = self.fw_status_text[ddns_value_start:
                                                ddns_value_end]

        # Primary will always come first, so using find should
        # find it's IP address, even if there's a warm spare
        # Using unique '{"public_ip":' to find primary IP address
        ip_start = self.fw_status_text.find("{\"public_ip\":")+14
        ip_end = self.fw_status_text[ip_start:].find('\"') + ip_start
        self.current_primary_ip = self.fw_status_text[ip_start: ip_end]
