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

from . import add_functions_as_methods, page_scrapers


@add_functions_as_methods(page_scrapers)
class DashboardBrowser:
    """API to interact with the Meraki Dashboard using the requests module.

    URLs can be generated from org eid and shard id:
    https://n<shard_id>.meraki.com/o/<eid>/manage/organization/

    Attributes:
        browser (MechanicalSoup): Main browser object to send data to dashboard

        vpn_vars (dict): List of VPN variables (does the browser need access
        to this?)

        orgs_dict (dict): A list of orgs/networks taken from administered_orgs
            See method scrape_administered_orgs for more information. Only
            difference from json blob is that network_eid key is replaced
            with network_id key

            = {
                <org#1 id>: {
                    'name'
                    'eid'
                    'node_groups': {
                        <network1_id> : {
                            ...
                        }
                        <network2_id> : {}
                        ...
                    }
                    ...
                }
                <org#2 id>: {}
                ...
            }

        org_qty (int): Number of organizations someone has access to. Once
            determined, it should be invariant.
        active_org_id (int): id of active org.
        active_network_id (int): id of active network.
        is_network_admin (string): If admin has networks but no org access

    """
    def __init__(self):
        """Initialize the browser and other class-wide variables."""
        super(DashboardBrowser, self).__init__()
        self.browser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},  # Use the lxml HTML parser
            raise_on_404=True,
            # User Agent String is for the Nintendo Switch because why not
            user_agent='Mozilla/5.0 (Nintendo Switch; ShareApplet) '
            'AppleWebKit/601.6 (KHTML, like Gecko) '
            'NF/4.0.0.5.9 NintendoBrowser/5.1.0.13341',)

        # Initialize organization dictionary {Name: Link} and
        # list for easier access. org_list is org_links.keys()
        self.orgs_dict = {}

        self.is_network_admin = False  # Most admins are org admins
        self.org_qty = 1
        self.active_org_id = 0
        self.active_network_id = 0
        self.pagetexts = {}

        # VPN VARS: Powershell Variables set to defaults
        # If it's set to '', then powershell will skip reading that parameter.
        self.vpn_vars = {}

    def attempt_login(self, username, password, tfa_code=None):
        """Verify whether the credentials are valid.

        Uses a MechanicalSoup object to send and submit username/password.
        The resultant URL is different for each auth eventuality and
        is used to identify each.

        Args:
            username (string): The username provided by the user
            password (string): The password provided by the user
            tfa_code (string): The tfa_code provided by the user

        Returns:
            (string): One of ('auth_error', 'sms_auth', 'auth_success')
              indicating the next login step.

        """
        # Navigate to login page
        try:
            self.browser.open(
                'https://account.meraki.com/login/dashboard_login')
        except requests.exceptions.ConnectionError as error:
            return type(error).__name__

        form = self.browser.select_form()
        self.browser["email"] = username
        self.browser["password"] = password
        form.choose_submit('commit')  # Click login button
        self.browser.submit_selected()  # response should be '<Response [200]>'
        print("browser url in attempt login " + str(self.browser.get_url()))

        # After setup, verify whether user authenticates correctly
        result_url = self.browser.get_url()
        # URL contains /login/login if login failed

        if result_url.find('/login/login') != -1:
            result_string = 'auth_error'
        # Two-Factor redirect: https://account.meraki.com/login/sms_auth?go=%2F
        elif result_url.find('sms_auth') != -1:
            if tfa_code:
                if self.tfa_submit_info(tfa_code):
                    result_string = 'auth_success'
                else:
                    result_string = 'auth_failure'
            else:
                result_string = 'sms_auth'
        else:
            result_string = 'auth_success'

        return result_string

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
        print("TFA Failure")
        return False

    # Fns that set up the browser for use
    ###########################################################################
    def org_data_setup(self):
        """Set up the orgs_dict for the rest of the program.

        This fn will set org qty correctly and add names and urls to org_data.

        NOTE: Don't set data for network-only admins as they don't have
        org-access. Network-only admin data is added in get_networks().

        Set:
            self.org_qty: We should know how many orgs from data on this page
            self.org_data: org names and urls will be added
        """
        # NOTE: Until you choose an organization, Dashboard will not let you
        # visit pages you should have access to
        page = self.browser.get_current_page()
        # 2+ orgs page : https://account.meraki.com/login/org_list?go=%2F
        if self.browser.get_url().find('org_list'):  # Admin orgs = 2
            self.bypass_org_choose_page(page)

        administered_orgs = self.scrape_administered_orgs()
        # Sort alphabetically by org name
        alphabetized_org_id_list = sorted(
            administered_orgs,
            key=lambda org_id_var: administered_orgs[org_id_var]['name'])

        for org_id in alphabetized_org_id_list:
            # Find active_org_id by finding the name of the org we're in
            if administered_orgs[org_id]['node_groups']:
                self.active_org_id = administered_orgs[org_id]['id']
            # Filter for wired as we only care about firewall networks
            self.orgs_dict[org_id] = self.filter_org_data(
                administered_orgs[org_id], ['wired'])

        self.active_network_id = list(
            self.orgs_dict[self.active_org_id]['node_groups'])[0]

    def bypass_org_choose_page(self, page):
        """Bypass page for admins with 2+ orgs that requires user input.

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
            'a', href=re.compile(r'/login/org_choose\?eid=.{6}'))
        # Get the number of orgs
        self.org_qty = len(org_href_lines)
        # Choose link for first org so we have something to connect to
        bootstrap_url = 'https://account.meraki.com' \
                        + org_href_lines[0]['href']
        self.browser.open(bootstrap_url)

    def scrape_administered_orgs(self):
        """Retrieve the administered_orgs json blob.

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
        base_url = self.browser.get_url().split('/manage')[0] + '/manage'
        administered_orgs_partial = '/organization/administered_orgs'
        administered_orgs_url = base_url + administered_orgs_partial
        print('administered_orgs url', administered_orgs_url)
        self.browser.open(administered_orgs_url)

        cookiejar = self.browser.get_cookiejar()
        response = requests.get(administered_orgs_url, cookies=cookiejar)
        administered_orgs = json.loads(response.text)
        if self.is_network_admin:
            self.org_qty = len(self.orgs_dict)

        return administered_orgs

    @staticmethod
    def filter_org_data(org_dict, network_types):
        """Filter the specifie dict by the network types provided.

        Args:
            org_dict (dict): A dict that looks like: administered_orgs[org_id].
            network_types (list): List of strings of target network types

        Returns:
            org_dict (dict): Dict containing all of an org's json except for
            node_groups types not included in network_types

            Also changes network_eid to network_id

        """
        filtered_dict = dict(org_dict)
        # Remove all networks so we can manually add the ones we want
        filtered_dict['node_groups'] = {}

        # eid is alphanumeric id for network
        for eid in org_dict['node_groups']:
            # Only add the network dicts for network types we care about
            eid_dict = org_dict['node_groups'][eid]
            is_filtered_type = eid_dict['network_type'] in network_types
            is_templated = eid_dict['is_template_child'] \
                or eid_dict['is_config_template']
            if is_filtered_type and not is_templated:
                # Same network ID as in API
                network_id = org_dict['node_groups'][eid]['id']
                filtered_dict['node_groups'][network_id] = \
                    org_dict['node_groups'][eid]

        return filtered_dict

    # Fns that operate independent of which URL the browser is at
    ###########################################################################
    def get_org_names(self):
        """Get a list of org names."""
        return [self.orgs_dict[org_id]['name'] for org_id in self.orgs_dict]

    def get_active_org_index(self):
        """Return the index of the active org by org_id."""
        return list(self.orgs_dict).index(str(self.active_org_id))

    def set_active_org_index(self, org_index):
        """Set the the org index to the param."""
        self.active_org_id = list(self.orgs_dict)[org_index]
        # If networks have not been retrieved for this org
        if not self.orgs_dict[self.active_org_id]['node_groups']:
            eid = self.orgs_dict[self.active_org_id]['eid']
            shard_id = str(self.orgs_dict[self.active_org_id]['shard_id'])
            new_org_url = 'https://n' + shard_id + '.meraki.com/o/' \
                          + eid + '/manage/organization/'

            self.browser.open(new_org_url)
            new_org_dict = self.scrape_administered_orgs()[self.active_org_id]
            filtered_org_dict = self.filter_org_data(new_org_dict, ['wired'])
            self.orgs_dict[self.active_org_id] = filtered_org_dict

    def set_active_network_index(self, network_index):
        """Set the active network by its index."""
        self.active_network_id = list(
            self.orgs_dict[self.active_org_id]['node_groups'])[network_index]

    def get_active_org_name(self):
        """Return the active org name."""
        return self.orgs_dict[self.active_org_id]['name']

    def get_network_names(self):
        """Get the network name for every network in the active org."""
        networks = self.orgs_dict[self.active_org_id]['node_groups']
        print('networks', networks)
        return [networks[network_id]['n'] for network_id in networks]

    def get_active_network_name(self):
        """Get the active network name."""
        return self.orgs_dict[self.active_org_id]['node_groups'][
            self.active_network_id]['n']

    def set_org_id(self, org_id):
        """Set the org_id.

        Args:
            org_id (int): Number that identifies an organization (unique)

        """
        if org_id in self.orgs_dict.keys():
            self.browser.active_org_id = org_id
        else:
            print("\nERROR:", org_id, "is not one of your org ids!"
                  "\nExiting...")
            exit()

    def set_network_id(self, network_id):
        """Set the network_id.

        Args:
            network_id (int): Number that identifies a network (unique)

        """
        org_id = self.active_org_id
        network_id_list = self.orgs_dict[org_id]['node_groups'].keys()
        if network_id in network_id_list:
            self.browser.active_network_id = network_id
        else:
            print("\nERROR:", network_id, "is not a network id in this org!"
                  "\nExiting...")
            exit()

    def set_org_name(self, org_name):
        """Set the org id by org name.

        If there are multiple matches (org names are not necessarily unique),
        choose the first one. Only the identifying part of the name needs to
        be entered (i.e. 'Organi' for 'Organiztion')
        """
        print(org_name)
        try:
            org_id = next(i for i in self.orgs_dict if org_name.lower()
                          in self.orgs_dict[i]['name'].lower())
            self.browser.active_org_id = org_id
        except StopIteration:
            print("\nERROR:", org_name, "was not found among your orgs!"
                  "\nExiting...")
            exit()

    def set_network_name(self, network_name):
        """Set the active network id by network name.

        If there are multiple matches (org names are not necessarily unique),
        choose the first one. Only the identifying part of the name needs to
        be entered (i.e. 'Netw' for 'Network')
        """
        try:
            # orgs_dict "t" key of network name has - instead of ' '
            org_id = self.active_org_id
            network_name = network_name.replace(' ', '-')
            net_dict = self.orgs_dict[org_id]['node_groups']
            network_id = next(
                network_id for network_id in net_dict
                if network_name.lower() in net_dict[network_id]['t'].lower())
            self.browser.active_network_id = network_id
        except StopIteration:
            print("\nERROR:", network_name, "was not found in this org!"
                  "\nExiting...")
            exit()

    def get_page_links(self):
        """Get all page links from current page's pagetext."""
        pagetext = self.browser.get_current_page().text
        json_text = re.findall(
            r'window\.initializeSideNavigation\([ -(*-~\r\n]*\)',
            pagetext,)[0][48:-1]
        json_dict = json.loads(json_text)
        # Format of this dict: {tab_menu: {tab: {'url': val, 'name': val}, ...
        page_url_dict = {}
        for tab_menu in range(len(json_dict['tab_menu']['tabs'])):
            for menu in ('Monitor', 'Configure'):
                category = json_dict['tab_menu']['tabs'][tab_menu]['name']
                page_url_dict[category] = {}
                qty_tabs = len(json_dict['tab_menu']['tabs'][
                    tab_menu]['menus'][menu]['items'])
                for tab in range(qty_tabs):
                    name = json_dict['tab_menu']['tabs'][tab_menu]['menus'][
                        menu]['items'][tab]['name']
                    url = json_dict['tab_menu']['tabs'][tab_menu]['menus'][
                        menu]['items'][tab]['url']
                    page_url_dict[category][name] = url

        return page_url_dict

    @staticmethod
    def get_mkiconf_vars(pagetext):
        """Return the mkiconf vars found on most dashboard pages.

        These variables are largely the same as administered orgs, but could
        be useful elsewhere. Keeping this here is in case I could use this of
        scraping method later. Check the regex below for the expected string.
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
            mki_string = \
                re.findall(r'[0-9a-zA-Z_\[\]\"]+\s*=\s[ -:<-~]*;', line)[0]
            # mki_key = <property>, mki_value = <JSON>
            mki_key, mki_value = mki_string.split(' = ', 1)
            if mki_value[-1] == ';':  # remove trailing ;
                mki_value = mki_value[:-1]
            # If the value is double quoted, remove both "s
            if mki_value[0] == '"' and mki_value[-1] == '"':
                mki_value = mki_value[1:-1]
            mki_dict[mki_key] = mki_value

        return mki_dict

    def open_route(self, target_route):
        """Redirect the browser to a page, given its route.

        Each page in dashboard has a route. If we're already at the page we
        need to be at to scrape, don't use the browser to open a page.

        Args:
            target_route (string): Text following '/manage' in the url that
                identifies (and routes to) a page.
        """
        current_url = self.browser.get_url()
        network_partial, _ = current_url.split('/manage')
        network_base = network_partial.split('.com/')[0]
        network_name = self.orgs_dict[self.active_org_id]['node_groups'][
            self.active_network_id]['t']
        eid = self.orgs_dict[self.active_org_id]['node_groups'][
            self.active_network_id]['eid']

        target_url = network_base + '.com/' + network_name + '/n/' + eid + \
            '/manage' + target_route
        # Don't go to where we already are!
        has_pagetext = target_url in self.pagetexts.keys()
        if self.browser.get_url() != target_url and not has_pagetext:
            try:
                self.browser.open(target_url)
                opened_url = self.browser.get_url()
                has_been_redirected = opened_url != target_url
                if has_been_redirected:
                    self.handle_redirects(target_url, opened_url)
            except mechanicalsoup.utils.LinkNotFoundError as error:
                url = network_partial + '/manage' + target_route
                print('Attempting to open', url, 'and failed.', error)

    @staticmethod
    def handle_redirects(target_url, opened_url):
        """On redirect, determine whether this is intended behavior."""
        print("ERROR: Redirected from intended route!"    
              "\nTarget url:", target_url,
              "\nOpened url:", opened_url,
              "\n\n")

        # Redirected from Security/Content filtering to Addressing & VLANs
        if 'filtering' in target_url and 'router' in opened_url:
            print("You are attempting to access content/security filtering "
                  "\nfor a firewall that is not licensed for it.")
        raise LookupError

    def get_node_settings_json(self):
        """Return the JSON containing node-data(route:/configure/settings)."""
        self.open_route('/configure/settings')
        current_url = self.browser.get_url()
        cookiejar = self.browser.get_cookiejar()
        json_text = requests.get(current_url, cookies=cookiejar).text
        return json.loads(json_text)

    def get_json_value(self, key):
        """Return a value for a key in a JSON blob in the HTML of a page.

        Args:
            key (string): The key we want the value for.
                Format: '<differentiating chars>"key"'
                Note a colon would be the next char of this string

        Returns:
            (String): The value of the passed-in key.

        """
        pagetext = self.browser.get_current_page().text
        key_location = pagetext.find(key)
        if key_location == -1:  # If key is not found
            return -1
        value_start = pagetext.find(key) + len(key) + 3
        value_end = pagetext[value_start:].find('\"') + value_start
        value = pagetext[value_start:value_end]
        print('For key:', key, 'retrieved value:', value)
        return value

    def get_network_users(self):
        """Get the network users.

        Location: Network-wide > Users

        JSON looks like so, with base64 secret as key for each user:
        {
            "base64 secret": {
                "secret": "base64 secret",
                "name": "First Last",
                "email": "name@domain.com",
                "created_at": unix_timestamp,
                "is_manage_user": true, # is user administrator
                "authed_networks": [  # client vpn/ssid authed network eid list
                      "abc1234",
                      "xyz5678",
                ]
            },
            "base64 secret": {
                "secret": "base64 secret",
                "name": "First Last",
                "email": "name@domain.com",
                ...
        }
        """
        self.open_route('/configure/guests')
        users_dict = json.loads(self.browser.get_current_page().text)

        for key in users_dict.keys():
            eid = self.orgs_dict[self.active_org_id]['node_groups'][
                self.active_network_id]['eid']
            self.orgs_dict[self.active_org_id][
                'node_groups'][self.active_network_id]['users'] = {
                    'name': users_dict[key]['name'],
                    'email': users_dict[key]['email'],
                    'is_admin': users_dict[key]['is_manage_user'],
                    'is_authorized': eid in users_dict[key]['authed_networks']}
