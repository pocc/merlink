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
from .pages.page_hunters import get_pagetext_json_value
from .pages.page_hunters import get_pagetext_mkiconf
from .pages.page_hunters import get_pagetext_links


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
        self.pagelinks = []

        # VPN VARS: Powershell Variables set to defaults
        # If it's set to '', then powershell will skip reading that parameter.
        self.vpn_vars = {}

    def login(self, username, password, tfa_code=None):
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
                    self.org_data_setup()
                else:
                    result_string = 'auth_failure'
            else:
                result_string = 'sms_auth'
        else:
            result_string = 'auth_success'
            self.org_data_setup()

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

        self.orgs_dict = self.scrape_json(
            '/organization/administered_orgs')
        # Filter for wired as we only care about firewall networks
        for org_id in self.orgs_dict:
            # Find active_org_id by finding the name of the org we're in
            if self.orgs_dict[org_id]['node_groups']:
                self.active_org_id = self.orgs_dict[org_id]['id']
                break

        base_url = self.browser.get_url().split('/manage')[0]
        eid = base_url.split('/n/')[1]
        self.active_network_id = eid
        print('url\n', self.get_url())

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

    def logout(self):
        """Logout out of Dashboard."""
        self.browser.open('https://account.meraki.com/login/logout')
        if '/login/dashboard_login' in self.get_url():
            print("Logout successful!")
        else:
            print("Logout NOT successful.")

    # Fns that get/set org info
    ###########################################################################
    def get_url(self):
        """Get the current url."""
        return self.browser.get_url()

    def get_pagetext(self):
        """Return the current pagetext."""
        return self.browser.get_current_page().text

    def get_org_names(self):
        """Get a list of org names."""
        orgs = [self.orgs_dict[org_id]['name'] for org_id in self.orgs_dict]
        return sorted(orgs)

    def get_active_org_name(self):
        """Return the active org name."""
        return self.orgs_dict[self.active_org_id]['name']

    def get_network_names(self, network_types=None):
        """Get the network name for every network in the active org."""
        # If no network types are specified, provide all.
        if not network_types:
            network_types = ['wired', 'switch', 'wireless',
                             'camera', 'systems_manager', 'phone']
        networks = self.orgs_dict[self.active_org_id]['node_groups']
        network_list = []
        for net_id in networks:
            is_desired_type = networks[net_id]['network_type'] in network_types
            is_template = networks[net_id]['is_config_template']
            if is_desired_type and not is_template:
                ntwk_name = networks[net_id]['n'].replace(' - appliance', '')
                network_list.append(ntwk_name)
        return sorted(network_list)

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
            self.active_org_id = org_id
            # If networks haven't been retrieved for this org (occurs once/org)
            if not self.orgs_dict[self.active_org_id]['node_groups']:
                org_eid = self.orgs_dict[self.active_org_id]['eid']
                shard_id = str(self.orgs_dict[self.active_org_id]['shard_id'])
                base = 'https://n' + shard_id + '.meraki.com/'
                new_org_url = base + 'o/' + org_eid + '/manage/organization/'
                self.browser.open(new_org_url)
                new_org_dict = self.scrape_json(
                    '/organization/administered_orgs')[self.active_org_id]
                self.orgs_dict[self.active_org_id] = new_org_dict
                # Set active network id by choosing first network.
                self.active_network_id = \
                    list(self.orgs_dict[org_id]['node_groups'])[0]
        else:
            print("\nERROR:", org_id, "is not one of your org ids!"
                  "\nExiting...\n")
            raise LookupError

    def set_network_id(self, network_id):
        """Set the network_id.

        Args:
            network_id (string): eid that identifies a network (unique)

        """
        org_id = self.active_org_id
        network_id_list = self.orgs_dict[org_id]['node_groups'].keys()
        if network_id in network_id_list:
            self.active_network_id = network_id
            # /configure/general is a route available to all network types.
            self.open_route('/configure/general', network_eid=network_id)
        else:
            print("\nERROR:", network_id, "is not a network id in this org!"
                  "\nExiting...")
            raise LookupError

    def set_org_name(self, org_name):
        """Set the org id by org name.

        If there are multiple matches (org names are not necessarily unique),
        choose the first one. Only the identifying part of the name needs to
        be entered (i.e. 'Organi' for 'Organiztion')
        """
        try:
            org_id = next(i for i in self.orgs_dict if org_name.lower()
                          in self.orgs_dict[i]['name'].lower())
            self.set_org_id(org_id)
        except StopIteration:
            print("\nERROR:", org_name, "was not found among your orgs!"
                  "\nExiting...\n")
            raise LookupError

    def set_network_name(self, network_name, network_type=None):
        """Set the active network id by network name.

        If there are multiple matches (org names are not necessarily unique),
        choose the first one. Only the identifying part of the name needs to
        be entered (i.e. 'Netw' for 'Network')

        Args:
            network_name (string): The name of the network to be set.
            network_type (string): Network_type if there is ambiguity
                due to a combined network. See below for valid types.
        """
        # If network type is not passed in, specify all.
        if not network_type:
            network_type = ['wired', 'switch', 'wireless',
                            'camera', 'systems_manager', 'phone']
        org_id = self.active_org_id
        chosen_network_id = ''
        net_dict = self.orgs_dict[org_id]['node_groups']
        for network_id in net_dict:
            ntwk_name = net_dict[network_id]['n'].lower()
            desired_network_type = \
                (net_dict[network_id]['network_type'] in network_type)
            if network_name.lower() in ntwk_name and desired_network_type:
                chosen_network_id = network_id
                print('chosen_network_id', chosen_network_id)
                break
        # If chosen_network_id was not found.
        if not chosen_network_id:
            print("\nERROR:", network_name, "was not found in this org!"
                  "\nExiting...\n")
            raise LookupError

        self.set_network_id(chosen_network_id)

    # Fns that open dashboard pages and get content from them.
    ###########################################################################
    def scrape_json(self, route):
        """Return the JSON containing node-data(route:/configure/settings)."""
        self.open_route(route)
        current_url = self.browser.get_url()
        cookiejar = self.browser.get_cookiejar()
        json_text = requests.get(current_url, cookies=cookiejar).text
        return json.loads(json_text)

    def open_route(self, route, category=None, network_eid=None, org_eid=None):
        """Redirect the browser to a page, given its route.

        Each page in dashboard has a route. If we're already at the page we
        need to be at to scrape, don't use the browser to open a page.
        For part variables, full URL might be something like:
        https://meraki.com/n/abc1234/configure/settings

        Args:
            route (string): Text following '/manage' in the url that
                identifies (and routes to) a page.
            category (bool): Redirect to correct network. For example,
                open_route('/configure/vpn_settings') is used on the switch
                subnetwork of a combined network that has a firewall. In this
                scenario, redirect to the firewall's page.
            network_eid (string): eid used to construct url when
                changing from org to network URLs
                (i.e. 'https:/n1.meraki.com/n/<network_id>/...')
            org_eid (string): eid used to construct url when
                changing from network to org URLs
                (i.e. 'https://n1.meraki.com/o/<org_id>/...')
        """
        if category:
            target_url = self.combined_network_redirect(route, category)
            if not target_url:
                raise LookupError
        else:
            current_url = self.browser.get_url()
            url_base = current_url.split('.com/')[0]
            if network_eid:
                url_partial = url_base + '.com/-/n/' + network_eid
            elif org_eid:
                url_partial = url_base + '.com/o/' + org_eid
            else:
                url_partial, _ = current_url.split('/manage')
            target_url = url_partial + '/manage' + route

        # Don't go to where we already are or have been!
        has_pagetext = [i for i in self.pagetexts.keys() if route in i]
        if self.get_url() != target_url and not has_pagetext:
            try:
                self.browser.open(target_url)
                print("Opening", target_url, "...")
                self.pagetexts[target_url] = self.browser.get_current_page()
                opened_url = self.browser.get_url()
                has_been_redirected = opened_url != target_url
                if has_been_redirected:
                    self.handle_redirects(target_url, opened_url)
            except mechanicalsoup.utils.LinkNotFoundError as error:
                print('Attempting to open', self.get_url(), 'with route',
                      route, 'and failed.', error)

    def combined_network_redirect(self, route, category):
        """Redirect to a different network type in a combined network."""
        pagelink_dict = get_pagetext_links(self.get_pagetext())
        for page in pagelink_dict[category]:
            page_url = pagelink_dict[category][page]
            if route in page_url:
                return page_url

    @staticmethod
    def handle_redirects(target_url, opened_url):
        """On redirect, determine whether this is intended behavior."""
        print("ERROR: Redirected from intended route! You may be accessing "
              "\na route that this network does not have"
              "\n(i.e. '/configure/vpn_settings' on a switch network).\n"
              "\nTarget url:", target_url,
              "\nOpened url:", opened_url,
              "\n")

        # Redirected from Security/Content filtering to Addressing & VLANs
        if 'filtering' in target_url and 'router' in opened_url:
            print("\nYou are attempting to access content/security filtering "
                  "\nfor a firewall that is not licensed for it.")
        raise LookupError
