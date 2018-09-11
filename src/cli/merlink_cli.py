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

# This docstring is used for docopt and requires specific formatting.
r"""
MERLINK

Usage:
  merlink.py
  merlink.py (--username <username>) [--password <password>]
  merlink.py (--username <username>) [--password <password>]
             [(--org-id <org_id> | --org-name <org_name>)
              (--network-id <network_id> | --network-name <network_name>)]
  merlink.py (-h | --help)
  merlink.py (-v | --version)

Options:
  -h, --help            Show this screen.
  -v, --version         Show MerLink's version.
  -u, --username        The Dashboard email account that you login with. This
                        account must have access to the intended firewall.
  -p, --password        Your Dashboard account password. If you do not want to
                        enter it visibly in the console, skip this option and
                        you will be asked securely with getparse.
  -o, --org-id          Your organization's ID. You can get this from the API.
  -n, --network-id      Your network's ID. You can get this from the API.
      --org-name        Your organization's name. Will fail if not unique.
      --network-name    Your network's name. Will fail if not unique.

Notes on Usages[0-2]:
  - Usage[0]        Launches the GUI. GUI > CLI featureset.
  - Usage[1]        Launch a menu-based TUI to select org and network.
  - Usage[2]        Creates the vpn and attempts a connection.

Examples:
  1. With org_id and network_id:
     $ merlink ֊֊username 'wile.e.coyote@acme.corp' \
               ֊֊password 'SuperGenius!' \
               ֊֊org-id 12345 \
               ֊֊network-id 67890
  2. With org_name and network_name:
     $ merlink ֊֊username 'wile.e.coyote@acme.corp' \
               ֊֊password 'SuperGenius!' \
               ֊֊org-name 'ACME Corp' \
               ֊֊network-name 'Wild West'

"""
import sys
import getpass

import docopt

from src.dashboard_browser.dashboard_browser import DashboardBrowser
from src.l2tp_vpn.vpn_connection import VpnConnection
from src.__version__ import __version__


class MainCli:
    """MerLink CLI : Less featured alternative to the GUI.

    Attributes:
        args (dict): A dict of all user-entered variables.
        browser (DashboardBrowser): Browser to hold state.
        username (string): Username to login with.
        password (string): Password to login with.

    """

    def __init__(self):
        """Initialize object and parse/store cli args."""
        super(MainCli, self).__init__()

        self.args = docopt.docopt(__doc__)
        self.browser = DashboardBrowser()

        # Determine which routine to do based on arguments
        if self.args['--version']:
            # 48w made by hand with ASCII characters
            with open("src/media/ascii-miles-48w.txt") as miles:
                miles = miles.read().replace('version', __version__.center(7))
                print('\n' + miles + '\n')
            sys.exit()

        # Required vars username/password
        self.username = self.args['<username>']
        if self.args['<password>']:
            self.password = self.args['<password>']
        else:
            self.password = getpass.getpass()

    def attempt_login(self):
        """Login to dashboard using username/password."""
        auth_result = self.browser.attempt_login(self.username, self.password)
        if auth_result == 'auth_error':
            print('ERROR: Invalid username or password. Now exiting...')
            sys.exit()
        elif auth_result == 'sms_auth':
            tfa_code = input("TFA code required for " + self.username + ": ")
            tfa_success = self.browser.tfa_submit_info(tfa_code.strip())
            if not tfa_success:
                print("ERROR: Invalid TFA code. Exiting...")
                sys.exit()
        elif auth_result == 'auth_success':
            print("Authentication success!")
            return
        elif 'ConnectionError' in str(type(auth_result)):
            print("""ERROR: No internet connection!\n\nAccess to the internet
                   is required for MerLink to work. Please check your network
                   settings and try again. Now exiting...""")
            sys.exit()

    def init_ui(self):
        """Start the program, having a browser and all relevant vars."""
        self.set_active_orgnet_ids(
            org_id=self.args['<org_id>'],
            network_id=self.args['<network_id>'],
            org_name=self.args['<org_name>'],
            network_name=self.args['<network_name>'],)

        self.browser.get_client_vpn_data()
        vpn_name = self.browser.get_active_network_name() + " - VPN"
        address = self.browser.get_client_vpn_address()
        psk = self.browser.get_client_vpn_psk()

        self.attempt_connection(
            [vpn_name, address, psk, self.username, self.password])

    def set_active_orgnet_ids(self, org_id, network_id,
                              org_name, network_name):
        """Set the active organization and network ids.

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
                    # orgs_dict "t" key of network name has - instead of ' '
                    network_name = network_name.replace(' ', '-')
                    net_dict = self.browser.orgs_dict[org_id]['node_groups']
                    network_id = next(
                        network_id for network_id in net_dict
                        if net_dict[network_id]['t'] == network_name)
                    self.browser.active_network_id = network_id
                except StopIteration:
                    self.alert_invalid_data("network name", network_name)
            except StopIteration:
                self.alert_invalid_data("organization name", org_name)
        else:
            self.tui()

    def tui(self):
        """Show MerLink Text User Interface when only user/pass are entered.

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
    def alert_invalid_data(var_type, var):
        """Let the user know they've entered invalid data and exit."""
        print("ERROR: Your " + var_type + ", '" + var + "' is not valid!")
        sys.exit()

    @staticmethod
    def get_user_input_from_list(list_name, list_type):
        """Show the user a numbered list and return the index they enter."""
        # Create a heading and underline it.
        print('\n' + list_type.upper() + 'S\n' + (len(list_type) + 1) * '=')
        # Get user org index choice and update the browser
        for index, item_name in enumerate(list_name):
            print(str(index) + '.', item_name)
        choice = int(input("\nEnter the " + list_type + " number: "))
        while choice not in range(len(list_name)):
            choice = int(
                input("Not a valid number! Please enter a number "
                      "between 0 and " + str(len(list_name)) + ": "))

        return choice

    @staticmethod
    def attempt_connection(vpn_data):
        """Create a VPN object and connect with it."""
        connection = VpnConnection(vpn_data=vpn_data, vpn_options={})
        connection.attempt_vpn()
