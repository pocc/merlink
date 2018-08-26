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

        ----

        vpn_vars (dict): List of VPN variables (does the browser need access
        to this?)

        org_dict (dict): A list of orgs/networks derived from administered_orgs
            See method scrape_administered_orgs for more information

            = {
                <org#1_id>: {
                    'name'
                    'networks': {
                        <network#1_name> : {
                            ...
                        }
                        <network2_name> : {}
                        ...
                    }
                    ...
                }
                <org#2_id>: {}
                ...
            }

        org_qty (int): Number of organizations someone has access to. Once
            determined, it should be invariant.
        active_org_index (int): Index of active org.
        active_network_index (int): Index of active network.
        is_network_admin (string): If admin has networks but no org access
    """
    def __init__(self):
        super(DataScraper, self).__init__()

        # Instantiate browser
        self.browser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},  # Use the lxml HTML parser
            raise_on_404=True,
            # User Agent String is for the Nintendo Switch because why not
            user_agent='Mozilla/5.0 (Nintendo Switch; ShareApplet) '
                       'AppleWebKit/601.6 (KHTML, like Gecko) '
                       'NF/4.0.0.5.9 NintendoBrowser/5.1.0.13341',
        )

        # Setup browser for use by other components
        self.username = ''
        self.password = ''

        # Initialize organization dictionary {Name: Link} and
        # list for easier access. org_list is org_links.keys()
        self.org_dict = {}
        self.org_urls = []

        self.is_network_admin = False  # Most admins are org admins
        self.org_qty = 0
        self.active_org_index = 0  # Default to first organization
        self.active_network_index = 0  # Default to first network

        # VPN VARS: Powershell Variables set to defaults
        # If it's set to '', then powershell will skip reading that parameter.
        self.vpn_vars = {}

    def attempt_login(self, username, password):
        """Verifies whether credentials are valid

        Uses a MechanicalSoup object to send and submit username/password.
        The resultant URL is different for each auth eventuality and
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
            tfa_code (string): The user-entered TFA string
            (should consist of 6 digits)
        """

        form = self.browser.select_form()
        print(self.browser.get_url())
        self.browser['code'] = tfa_code
        form.choose_submit('commit')  # Click 'Verify' button
        self.browser.submit_selected()

        active_page = self.browser.get_current_page().text
        # Will return -1 if it is not found
        if active_page.find("Invalid verification code") == -1:
            print("TFA Success")
            return True
        else:
            print("TFA Failure")

    def count_admin_orgs(self):
        """Count whether the admin has access to 0, 1, or 2+ orgs

        This fn will set org qty correctly and add names and urls to org_data.

        NOTE: Don't set data for network-only admins as they don't have
        org-access. Network-only admin data is added in get_networks().

        Set:
            self.org_qty: We should know how many orgs from data on this page
            self.org_data: org names and urls will be added
        """

        print("in fn [count_admin_orgs]")

        # NOTE: Until you choose an organization, Dashboard will not let you
        # visit pages you should have access to
        page = self.browser.get_current_page()
        # Use pagetext variable so we can have a string we can use slices with
        pagetext = page.text
        # Found in HTML for administrators with access to only 1 org
        # org_str is ONLY found for one org admins (-1 means string isn't found)
        is_one_org_admin = pagetext.find("org_str") != -1
        if is_one_org_admin:  # Admin orgs = 1
            self.org_qty = 1
            # This should be present in EVERY dashboard page
            org_name_start = pagetext.find("Mkiconf.org_name") + 20
            org_name_end = org_name_start + pagetext[org_name_start:].find('"')
            one_org_name = pagetext[org_name_start: org_name_end]
            self.org_dict[one_org_name] = {'url': self.browser.get_url()}

        # 2+ orgs choice page : https://account.meraki.com/login/org_list?go=%2F
        elif 'org_list' in self.browser.get_url():  # Admin orgs = 2
            self.bypass_org_choose_page(page)

        else:  # Admin orgs = 0 (i.e. network-only admin)
            # Org name for those who can't see the org
            self.org_dict["Plato's Cave org"] = {}
            self.org_dict["Plato's Cave org"]['url'] = self.browser.get_url()

    def bypass_org_choose_page(self, page):
        """Bypass page for admins with 2+ orgs that normally requires user input

        Admins with 2+ orgs are shown a page where they need to choose an
        organization to enter. This function will follow the link associated
        with the alphabetically first organization and then gather org/network
        info so we have something to show the user.

        Args:
            page (BeautifulSoup): Soup object that we can use to load a link
            to the first org.
        """
        # Get a list of all org links. href comes before a link in HTML.
        org_href_lines = page.findAll(
            'a', href=re.compile('/login/org_choose\?eid=.{6}'))
        # Get the number of orgs
        self.org_qty = len(org_href_lines)

        # For each HTML line in a list containing name and org link part
        # Get the org name and create full org link
        for href_line in org_href_lines:
            org_name = href_line.string
            login_link = 'https://account.meraki.com' + href_line['href']
            # Open each login link so that it redirects to a usable URL
            self.browser.open(login_link)
            org_link = self.browser.get_url()
            self.org_urls.append(org_link)
            print('Org', org_name, 'at', org_link)

        # Open the browser to the first org so we have data to show user
        self.browser.open(self.org_urls[0])

    @staticmethod
    def get_mkiconf_vars(pagetext):
        """Most dashboard pages have mkiconf vars. This fn returns them.

        These variablesa are largely the same as administered orgs, but could
        be useful elsewhere. Check the regex below for the expected string.
        The format will look like this:

            Mkiconf.action_name = "new_wired_status";
            Mkiconf.log_errors = false;
            Mkiconf.eng_log_enabled = false;
            Mkiconf.on_mobile_device = false;

        Essentially  Mkiconf.<property> = <JSON>;

        Args:
            pagetext (string): Text of a webpage

        Returns:
            (dict) All available Mkiconf vars.
        """
        mki_lines = re.findall(' Mkiconf[ -:<-~]*;', pagetext)
        mki_dict = {}
        for line in mki_lines:
            mki_string = re.findall('[0-9a-zA-Z_]+\s*=\s[ -:<-~]*;', line)[0]
            # mki_key = <property>, mki_value = <JSON>
            mki_key, mki_value = mki_string.split(' = ', 1)
            mki_dict[mki_key] = mki_value

        return mki_dict

    def scrape_administered_orgs(self):
        """Retrieve the administered_orgs json blob

        For orgs that are not being accessed by the browser, node_groups = {}.
        For this reason, the administered_orgs json needs to be retrieved every
        time the user goes to a different organization.

        * get_networks should only be called on initial startup or if a
          different organization has been chosen
        * browser should have clicked on an org in the org selection page so we
          can browse relative paths of an org

        administered_orgs (dict): A JSON blob provided by /administered_orgs
            that contains useful information about orgs and networks. An eid
            for an org or network is a unique way to refer to it.

            = {
                <org#1 org_id>: {
                    'name' : <org name>
                    'url': <url>,
                    'node_groups': {
                        <network#1 eid> : {
                            'n': <name>
                            'has_wired': <bool>
                            ...
                        }
                        <network#2 eid> : {}
                        ...
                    }
                    ...
                }
                <org#2 org_id>: {}
                ...
            }
        """

        base_url = self.get_base_url(self.get_url())
        administered_orgs_partial = '/organization/administered_orgs'
        administered_orgs_url = base_url + administered_orgs_partial
        print(administered_orgs_url)
        self.browser.open(administered_orgs_url)

        cj = self.browser.get_cookiejar()
        response = requests.get(administered_orgs_url, cookies=cj)
        administered_orgs = json.loads(response.text)
        self.org_dict = self.filter_orgs_dict(administered_orgs, 'wired')
        if self.is_network_admin:
            self.org_qty = len(self.org_dict)

        print("\nI stole the cookie jar and it's right here:", cj,
              "\nAdministered Orgs =>", json.dumps(administered_orgs,
                                                   indent=4, sort_keys=True),
              "\nactive org ", self.get_active_org_name())

    @staticmethod
    def filter_orgs_dict(orgs_dict, network_type):
        """Return a filtered orgs_dict with just the network_type contained

        Does:
            * Changes network eid to the name of the network for usability
            * Removes all but network_type specified from dict
        Why:
            To iterate over only the relevant network types in other methods

        Args:
            orgs_dict (dict): The dict to be filtered
            network_type (string): The network_type to filter by

        Returns:
            A filtered orgs_dict with just the network_type in node_groups

        NOTE: Requires orgs_dict to be in Meraki JSON format.
        NOTE: Storing administered_orgs in a dict should not take up more
        than 1MB of RAM.
        """
        # Returning this dict
        filtered_dict = {}
        for org in orgs_dict:
            # Copy everything over except the node_groups we want to filter
            filtered_dict[org] = {
                key: val for key, val in orgs_dict[org].items()
                if key != 'node_groups'}
            filtered_dict[org]['node_groups'] = {}
            for network_eid in orgs_dict[org]['node_groups']:
                node_group_data = orgs_dict[org]['node_groups'][network_eid]
                # If it's a config template, it doesn't contain devices
                device_type_in_network = node_group_data['network_type'] == \
                    network_type and not node_group_data['is_config_template']
                if device_type_in_network:
                    filtered_dict[org]['node_groups'][network_eid] = \
                        node_group_data

        return filtered_dict

    def scrape_network_vars(self, network_index):
        """Change the current network."""
        self.active_network_index = network_index
        self.scrape_psk()
        self.scrape_ddns_and_ip()

    def scrape_psk(self):
        """Scrape Client VPN PSK"""
        client_vpn_url = self.get_base_url(self.get_url()) \
            + '/configure/client_vpn_settings'
        print("Client VPN URL " + client_vpn_url)
        client_vpn_text = self.browser.get(client_vpn_url).text
        client_vpn_soup = bs4.BeautifulSoup(client_vpn_text, 'lxml')
        self.vpn_vars['psk'] = client_vpn_soup.find("input", {
            "id": "wired_config_client_vpn_secret", "value": True})['value']

    def scrape_ddns_and_ip(self):
        """Scrape the ddns and primary ip address."

        This method gets ddns and ip values for the active network. This
        method should ONLY be called if the user has hit the connect button
        """
        fw_status_url = self.get_base_url(self.get_url()) \
            + '/nodes/new_wired_status'
        fw_status_text = self.browser.get(fw_status_url).text

        # ddns value can be found by searching for '"dynamic_dns_name"'
        ddns_value_start = fw_status_text.find("dynamic_dns_name")+19
        ddns_value_end = fw_status_text[ddns_value_start:].find('\"') \
            + ddns_value_start
        self.vpn_vars['ddns'] = \
            fw_status_text[ddns_value_start:ddns_value_end]

        # Primary will always come first, so using find should
        # find it's IP address, even if there's a warm spare
        # Using unique '{"public_ip":' to find primary IP address
        ip_start = fw_status_text.find("{\"public_ip\":")+14
        ip_end = fw_status_text[ip_start:].find('\"') + ip_start
        self.vpn_vars['ip'] = fw_status_text[ip_start: ip_end]
        print('scraped ddns', self.vpn_vars['ddns'],
              'ip', self.vpn_vars['ip'])

    # Fns that operate independent of which URL the browser is at
    ###########################################################################
    def get_browser(self):
        """Get the MechanicalSoup object with associated login cookies."""
        return self.browser

    def get_url(self):
        """Get the current URL"""
        print("browser url in get_url" + str(self.browser.get_url()))
        return self.browser.get_url()

    def get_org_list(self):
        """Get this administrator's org list."""
        org_list = []
        for i in range(self.org_qty):
            org_values_list = list(self.org_dict.values())
            org_name = org_values_list[i]['name']
            org_list.append(org_name)
        return org_list

    def get_org_dict_by_index(self, index):
        """Return an org's dict by its index"""
        return list(self.org_dict.values())[index]

    # get_active fns get info about the org the browser is at
    ###########################################################################
    def get_active_org_index(self):
        """Return the org index."""
        return self.active_org_index

    def set_active_org_index(self, org_index):
        """Set the the org index to the param."""
        self.browser.open(self.org_urls[org_index])
        self.active_org_index = org_index

    def get_active_org_name(self):
        """Get the active org name."""
        return self.get_org_list()[self.active_org_index]

    def get_active_org_dict(self):
        """Get the active org dict."""
        active_org_id = list(self.org_dict)[self.active_org_index]
        return self.org_dict[active_org_id]

    def get_active_org_networks(self):
        """Get the active network names"""
        network_names = []
        # If node_groups is populated, then network names can be extracted
        if self.get_active_org_dict()['node_groups']:
            eid_dict = self.get_active_org_dict()['node_groups']
            # Iterate over all eid keys to get network names
            for i in range(len(eid_dict)):
                network_name = self.get_active_network_dict_by_index(i)
                network_names.append(network_name)

        return network_names

    def get_active_network_dict_by_index(self, index):
        """Get dict for a network given an index."""
        eid = list(self.get_active_org_dict()['node_groups'])[index]
        return self.get_active_org_dict()['node_groups'][eid]['n']

    def get_active_network_dict(self):
        """Get dict for a n"""
        print('active network index', self.active_network_index)
        return self.get_active_network_dict_by_index(self.active_network_index)

    @staticmethod
    def get_base_url(url):
        """Return the network-based base URL up to '/manage'"""
        base_url = url.split('/manage')[0] + '/manage'
        return base_url
