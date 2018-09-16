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
import sys
import os

from .dashboard import DashboardBrowser


class ClientVpnBrowser(DashboardBrowser):
    """Client VPN class."""

    def __init__(self):
        """Initialize Client VPN object."""
        super(ClientVpnBrowser, self).__init__()
        self.vpn_vars = ''

    def get_client_vpn_psk(self):
        """Return the Client VPN PSK."""
        psk = self.orgs_dict[self.active_org_id]['node_groups'][
            self.active_network_id]['client_vpn_secret']
        return psk

    def get_client_vpn_address(self):
        """Return the psk and address.

        Use the public_contact_point Mkiconf var to get address.
        It is DDNS name if DDNS is enabled and is otherwise IP address.
        public_contact_point is on. (route:/configure/router_settings)
        It's gone in new view, so let's put this on hold.
        """
        self.open_route('/nodes/new_wired_status')
        using_ddns = (self.get_json_value('dynamic_dns_enabled') == 'true')
        if using_ddns:
            address = self.get_json_value('dynamic_dns_name')
        else:
            address = self.get_json_value('{"public_ip')

        return address

    def get_client_vpn_data(self):
        """Return client VPN variables."""
        # If one of the expected keys has not been set in this network dict,
        # set variables. Otherwise, we're pulling data for the same network.
        if 'client_vpn_enabled' not in self.orgs_dict[self.active_org_id][
                'node_groups'][self.active_network_id].keys():
            var_dict = self.get_node_settings_json()
            client_vpn_vars = [
                'client_vpn_active_directory_servers',
                'client_vpn_auth_type',
                'client_vpn_dns',
                'client_vpn_dns_mode',
                'client_vpn_enabled',
                'client_vpn_pcc_auth_tags',
                'client_vpn_radius_servers',
                'client_vpn_site_to_site_mode',
                'client_vpn_site_to_site_nat_enabled',
                'client_vpn_site_to_site_nat_subnet',
                'client_vpn_subnet',
                'client_vpn_wins_enabled',
                'client_vpn_wins_servers',
                'client_vpn_enabled',
                'client_vpn_secret',
            ]

            for var in client_vpn_vars:
                self.orgs_dict[self.active_org_id]['node_groups'][
                    self.active_network_id][var] = var_dict['wdc'][var]

    def is_client_vpn_enabled(self):
        """Check basic client vpn things."""
        # Is client vpn enabled?)
        return self.orgs_dict[self.active_org_id]['node_groups'][
            self.active_network_id]['client_vpn_enabled']

    def troubleshoot_client_vpn(self):
        """Troubleshoot Client VPN.

        Six tests are used to see what might be wrong.
            check_firewall_page_errors
                1. Is the user behind the firewall?
                2. Is there a firewall in the network?
                3. Is the firewall online?
            check_nat_rules
                4. Is 500 + 4500 traffic being forwarded?
                5. Is 500 + 4500 traffic being natted?
            check_firewall_connectivity
                6. Can the client ping the firewall?
        """
        # If the user is behind their firewall, they will not be able to
        # connect (and a VPN connection would be pointless.)
        errors = ''
        errors += self.check_firewall_page_errors()
        errors += self.check_nat_rules()
        errors += self.check_firewall_connectivity()

        if errors:
            return errors
        return "No common misconfigurations found."

    def check_firewall_page_errors(self):
        """Check 3 things using info from Appliance Status page.

        1. Is the user behind the firewall?
        2. Is there a firewall in the network?
        3. Is the firewall online?
        """
        errors = ''
        self.open_route('/nodes/new_wired_status')
        client_public_ip = self.get_json_value('request_ip')
        firewall_public_ip = self.get_json_value('{"public_ip')
        if client_public_ip == firewall_public_ip:
            errors += "\nERROR: You cannot connect to your firewall if " \
                      "you are behind it!"
        # 0 = online, 2 = temporarily offline, 3 = offline for a week+
        firewall_status_code = self.get_json_value("status#")
        if firewall_status_code == -1:
            errors += "\nERROR: There is no firewall in this network!"
        elif firewall_status_code == '0':
            errors += "\nERROR: Your firewall is offline!"
        return errors

    def check_nat_rules(self):
        """Check whether a nat or port forwarding rule is causing vpn failure.

        An IPSEC connection uses UDP port 500, and UDP port 4500 if NAT.

        Sample JSON example of bad firewall ports:
        "port_forwarding_settings":[{"ip":"10.0.0.1","allowed_ips":["any"],
            "name":"break client vpn","proto":"tcp","public_port":"500",
            "local_port":"500","inet":"Both"}],
        "one_to_one_nat_settings":[{"name":"alpha","lanip":"10.0.0.1",
            "uplink":"1","allowed_inbound":[{"proto":"udp","dst_port":["500",
            "4500"],"allowed_ips":["any"]}],"wanip":"4.0.0.1"}]
        """
        errors = ''
        self.open_route('/configure/firewall')
        pagetext = self.browser.get_current_page().text
        port_forwarding_ipsec_ports = re.search(
            r'"udp","public_port":"[4]?500"', pagetext)
        if port_forwarding_ipsec_ports:
            errors += "\nERROR: You are port forwarding " \
                      "IPSEC udp ports 500 and 4500!"
        natting_ipsec_ports = re.search(
            r'"dst_port":\[[0-9",]*"[4]?500"[0-9",]*\]', pagetext)
        if natting_ipsec_ports:
            errors += "\nERROR: You are natting " \
                      "IPSEC udp ports 500 and 4500!"
        return errors

    def check_firewall_connectivity(self):
        """Check whether the user can ping the firewall.

        Connectivity between sites is not necessarily transitive.
        """
        # Verify whether firewall is reachable by pinging 4 times
        # If at least one ping that made it, mark this test as successful.
        address = self.get_client_vpn_address()
        if sys.platform == 'win32':  # Identifies any form of Windows
            # ping 4 times every 1000ms
            ping_string = "ping " + address
        else:  # *nix of some kind
            # ping 4 times every 200ms
            ping_string = "ping -c 5 -i 0.2 " + address
        ping_response = os.system(ping_string)
        # Non-0 ping responses mean failure. Error codes are OS-dependent.
        if ping_response != 0:
            # Failure error dialog and then return
            return "\nERROR: Cannot ping device!"
        return ""
