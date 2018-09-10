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

"""
merlink
Usage:
  merlink
  merlink (--username) [--password]
  merlink (--username) [--password] (--org-id | --org-name) \
(--network-id | --network-name)
  merlink (-h | --help)
  merlink (-v | --version)

Options:
  -h --help         Show this screen.
  -v --version      Show MerLink's version.
  --username        The Dashboard email account that you login with. This \
account should have access to the firewall to which you want to connect.
  --password        Your Dashboard account password. If you want to be shoulder\
-surfing-safe, do not specify this option and you will be asked securely.
  --org-id          Your organization's ID. You can get this from the API.
  --network-id      Your network's ID. You can get this from the API.
  --org-name        Your organization's name. Will fail if it is not unique.
  --network-name    Your network's name. Will fail if it is not unique.

Notes on Usages[0-2]:
  - Usage[0]        Launches the GUI. GUI > CLI featureset.
  - Usage[1]        Launch a menu-based TUI to select org and network.
  - Usage[2]        Creates the vpn and attempts a connection.
"""
import docopt
import getpass
import sys

from src.dashboard_browser.dashboard_browser import DashboardBrowser
from src.modules.vpn_connection import VpnConnection
from src.__version__ import __version__


class MainCli:
    """
    MerLink CLI

    Command line options spec based on expected use cases:

    1. TUI mode: If dashboard username/password are known
    Usage: merlink --username <username> --password <password>
    << Organizations and networks are shown to user
    >> User selects the network they would like to connect to
    << program creates and connects vpn

    2. CLI ORG/NET ID/NAME mode: If username + password of dashboard admin,
    organization name, and network name are already known
    Usage: merlink --username <username> --password <password> --org-name
    <organization> --network-name <network>

    ex. merlink --username 'wile.e.coyote@acme.corp' --password 'SuperGenius!'
        --org-id 12345 --network-id 67890

    ex. merlink --username 'wile.e.coyote@acme.corp' --password 'SuperGenius!'
        --org-name 'ACME Corp' --network-name 'Wild West'

    NOTE: If there are conflicts in organization or network names, there will
    be an error and it may be wise to use org-id/network-id instead.

    3. No dashboard CLI mode: Enter all information manually (no user/pass)
    Usage: merlink  --username <username> --password <password>
    --vpn-name <vpn name> --address <server IP/DDNS> --psk <PSK>

    ex. merlink --username 'wile.e.coyote@acme.corp' --password 'SuperGenius!'
        --vpn-name 'ACME VPN' --address 'acme.corp' --psk '@AnyCost'

    """

    def __init__(self):
        super(MainCli, self).__init__()

        args = docopt.docopt(__doc__)
        print(args)
        self.choose_subprogram(args)
        self.browser = DashboardBrowser()

    def choose_subprogram(self, args):
        """Determine which routine to do based on arguments"""

        if args['--version']:
            print("Welcome to Merlink " + __version__ + "!")
            # 48w made by hand with ASCII characters
            with open("src/media/ascii-miles-48w.txt") as miles:
                miles = miles.read().replace('version', __version__.center(7))
                print(miles)
            sys.exit()

        # Required vars username/password
        username = args['--username']
        if args['--password']:
            password = args['--password']
        else:
            password = getpass.getpass()
        self.login_prompt(username, password)

        self.set_active_orgnet_ids(
            org_id=args['--org_id'],
            network_id=args['--network-id'],
            org_name=args['--org_name'],
            network_name=args['--network_name'],
        )

        vpn_name = self.browser.get_active_network_name() + " - VPN"
        address = self.browser.get_client_vpn_address()
        psk = self.browser.get_client_vpn_psk()

        self.attempt_connection([vpn_name, address, psk, username, password])

    @staticmethod
    def alert_invalid_data(var_type, var):
        """Let the user know they've entered invalid data and exit."""
        print("ERROR: Your " + var_type + ", '" + var + "' is not valid!")
        sys.exit()

    def set_active_orgnet_ids(self, org_id, network_id, org_name, network_name):
        """Set the active organization and network ids

        This fn is necessary to set the browser to open the correct network.

        Args:
            org_id (int): Number that identifies an organization (unique)
            network_id (int): Number that identifies a network (unique)
            org_name (string): Name of an organization (usually unique)
            network_name (string): Name of a network (unique)
        """
        has_orgnet_ids = org_id and network_id
        has_orgnet_names = org_name and network_name
        if has_orgnet_ids:
            if org_id in self.browser.orgs_dict.keys():
                self.browser.active_org_id = org_id
                network_id_list = self.browser.orgs_dict[org_id][
                    'node_groups'].keys()
                if network_id in network_id_list:
                    self.browser.active_network_id = network_id
                else:
                    self.alert_invalid_data("Your network_id", network_id)
            else:
                self.alert_invalid_data("Your org_id", org_id)
        elif has_orgnet_names:
            # For both org and network name, find the first instance if it
            # exists. If it does not, throw a StopIteration error and quit.
            try:
                org_dict = self.browser.orgs_dict
                org_id = next(i for i in org_dict
                              if org_dict[i]['name'] == org_name)
                self.browser.active_org_id = org_id
                try:
                    # orgs_dict "t" version of network name has - instead of ' '
                    network_name = network_name.replace(' ', '-')
                    network_dict = self.browser.orgs_dict[org_id]['node_groups']
                    network_id = next(
                        network_id for network_id in network_dict
                        if network_dict[network_id]['t'] == network_name)
                    self.browser.active_network_id = network_id
                except StopIteration:
                    self.alert_invalid_data("network name", network_name)
            except StopIteration:
                self.alert_invalid_data("organization name", org_name)
        else:
            self.tui()

    def login_prompt(self, username, password):
        """Login to dashboard using username/password

        Args:
            username (string): Dashboard admin email associated with account
            password (string): Password used to login with username
        """
        auth_result = self.browser.attempt_login(username, password)
        if auth_result == 'auth_error':
            print('ERROR: Invalid username or password. Now exiting...')
            sys.exit()
        elif auth_result == 'sms_auth':
            tfa_code = input("TFA code required for " + username + ":").strip()
            tfa_success = self.browser.tfa_submit_info(tfa_code)
            if not tfa_success:
                print("ERROR: Invalid TFA code. Exiting...")
                sys.exit()
        elif auth_result == 'auth_success':
            self.tui()
        elif 'ConnectionError' in str(type(auth_result)):
            print('ERROR: No internet connection!\n\nAccess to the internet is '
                  'required for MerLink to work. Please check your network '
                  'settings and try again. Now exiting...')
            sys.exit()

    def tui(self):
        """Shows MerLink Text User Interface when only user/pass are entered.

        Usage:
            merlink --username <username> --password <password>

        Operation:
            1. Show user list of orgs
            2. User chooses an org
            3. Show user list of networks in that org
            4. User chooses network
            5. MerLink connects

        Args:
            Will trigger only iff --username and --password are specified.
        """
        org_list = self.browser.get_org_names()
        org_index = self.get_user_input_from_list(org_list, "organization")
        self.browser.set_active_org_index(org_index)

        network_list = self.browser.get_network_names()
        network_index = self.get_user_input_from_list(network_list, "network")
        self.browser.set_active_network_index(network_index)

    @staticmethod
    def get_user_input_from_list(list_name, list_type):
        """Show the user a numbered list and return the index they enter"""
        # Get user org index choice and update the browser
        for index, org_name in enumerate(list_name):
            print(str(index) + '.', org_name)
        choice = input("\nEnter the " + list_type + " number:")
        while choice not in range(len(list_name)):
            choice = input("Not a valid number! Please enter a number between "
                           "0 and " + str(len(list_name)) + ":")

        return choice

    @staticmethod
    def attempt_connection(vpn_data):
        """Create a VPN object and connect with it."""
        connection = VpnConnection(
            vpn_data=vpn_data,
            vpn_options=[])
        connection.attempt_vpn()