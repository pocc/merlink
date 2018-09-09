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

"""Provides a CLI for MerLink"""
import argparse
import sys

from src.cli.cli_modal_prompts import CliModalPrompts
from src.dashboard_browser.dashboard_browser import DashboardBrowser
from src.modules.vpn_connection import VpnConnection


class MainCli:
    """
    MerLink CLI
    Based on ncurses


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

        self.parse_options()
        self.messages = CliModalPrompts()
        self.browser = DashboardBrowser()

    @staticmethod
    def parse_options():
        """Parses argparse options and then calls other parts of program."""

        parser = argparse.ArgumentParser(prog='MERLINK')
        parser.add_argument("-v", "--verbose",
                            help="increase output verbosity",
                            action="store_true")

        required_group = parser.add_argument_group("required arguments")
        orgnet_id_group = parser.add_argument_group("org/net id")
        orgnet_name_group = parser.add_argument_group("org/net name")
        manual_entry_group = parser.add_argument_group("manual entry")
        #######################################################################
        required_group.add_argument(
            "-u", "--username",
            help="The Dashboard email account that you login with. This "
                 "account should have access to the firewall to which "
                 "you want to connect.",
            required=True)
        required_group.add_argument(
            "-p", "--password",
            help="Your Dashboard account password.",
            required=True)
        #######################################################################
        orgnet_id_group.add_argument(
            "-o", "--org-id",
            help="The Dashboard organization id for the firewall. "
                 "To get this value for your firewall, use the API",
            required=False)
        orgnet_id_group.add_argument(
            "-n", "--network-id",
            help="The Dashboard network id for the firewall. "
                 "To get this value for your firewall, use the API.",
            required=False)
        #######################################################################
        orgnet_name_group.add_argument(
            "--org-name",
            help="The name of the Dashboard org that contains the firewall. "
                 "If this org name is not unique, this parse tree will fail "
                 "(use --org-id instead).",
            required=False)
        orgnet_name_group.add_argument(
            "--network-name",
            help="The name of the Dashboard network that contains this firewall"
                 ". If the org name is not unique, this parse tree will fail "
                 "(use --network-id instead).",
            required=False)
        #######################################################################
        manual_entry_group.add_argument(
            "-a", "--address",
            help="The DDNS/IP address of your firewall.",
            required=False)
        manual_entry_group.add_argument(
            "-k", "--psk",
            help="The pre-shared key.",
            required=False)
        manual_entry_group.add_argument(
            "-m", "--vpn-name",
            help="The name given locally to this VPN connection.",
            required=False)

        args = parser.parse_args()
        if args.verbose:
            print("Welcome to Merlink Verbose!")
            # 60w and 80w ASCII Miles generated by
            # https://www.ascii-art-generator.org/
            # 48w made by hand with ASCII characters
            with open("src/media/ascii-miles-48w.txt", 'r') as miles:
                print(miles.read())
            sys.exit()

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
            self.tui(username, password)
        elif 'ConnectionError' in str(type(auth_result)):
            print('ERROR: No internet connection!\n\nAccess to the internet is '
                  'required for MerLink to work. Please check your network '
                  'settings and try again. Now exiting...')
            sys.exit()

    def tui(self, username, password):
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

        vpn_name = network_list[network_index] + " - VPN"
        ddns = self.browser.get_client_vpn_address()
        psk = self.browser.get_client_vpn_psk()
        connection = VpnConnection(
            vpn_data=[vpn_name, ddns, psk, username, password],
            vpn_options=[])
        connection.attempt_vpn()

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

    def get_user_action(self):
        """Gets the user's next action

        Currently not implemented but mirrored in main_window"""

        pass

    def add_vpn(self):
        """Adds a vpn by name

        Currently not implemented but mirrored in main_window"""

        pass

    def connect_vpn(self, *vpn_vars):
        """Connects using the specified vpn connection

        Currently not implemented but mirrored in main_window"""

        pass

    def show_result(self, result):
        """Shows the result of the vpn connection to the console

        Currently not implemented but mirrored in main_window"""

        pass

    def troubleshoot_vpn(self):
        """Provides an interface to interact with troubleshooting functionality.

        Currently not implemented but mirrored in main_window"""

        pass
