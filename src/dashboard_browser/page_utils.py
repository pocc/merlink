# -*- coding: utf-8 -*-
"""Utilities to scrape elements from / input text into a page."""


class MxPageUtils:
    """Utilities to scrape elements from / input text into a page.
    Requirements:
        * Network page is loaded in the browser
        * Browser is passed into this function
    """
    def __init__(self, browser):
        self.browser = browser

    def get_mx_vlans_configured(self):
        """Get the bool of whether VLANs are enabled

        Location: Security Appliance > Addressing & VLANs > Routing
        """
        self.browser.open_route(route='/configure/router_settings')
        dropdown_value = self.get_mx_dropdown_value(
            self.browser.get_current_page(),
            var_id='wired_config_vlans_enabled',
        )
        return dropdown_value == 'Enabled'

    def get_mx_ddns_enabled(self):
        """Get the bool of whether DDNS is enabled

        Location: Security Appliance > Addressing & VLANs > Dynamic DNS
        """
        self.browser.open_route(route='/configure/router_settings')
        dropdown_value = self.get_mx_dropdown_value(
            self.browser.get_current_page(),
            var_id='wired_config_dynamic_dns_enabled',
        )
        return dropdown_value == 'Enabled'

    def get_mx_ddns_configurable_substring(self):
        """Users can set the first part of an appliance's ddns. Scrape that.

        Location: Security Appliance > Addressing & VLANs > Dynamic DNS

        Sample HTML for DDNS name:
            <input id="wired_config_dynamic_dns_label" maxlength="32"
            name="wired_config[dynamic_dns_label]" size="25" type="text"
            value="network-name-wired">

        Sample ddns from above HTML: network-name-wired-abcdefghij.dynamic-m.com
        """
        self.browser.open_route(route='/configure/router_settings')
        return self.get_input_var_value(
            soup=self.browser.get_current_page(),
            var_id='wired_config_dynamic_dns_label',
        )

    def set_mx_ddns_configurable_substring(self, ddns_substring):
        """Set the first part of an appliance's ddns with specified string.

        Location: Security Appliance > Addressing & VLANs > Dynamic DNS

        Given this ddns name: network-name-wired-abcdefghij.dynamic-m.com, the
            configurable substring would be 'network-name-wired'
        """
        self.browser.open_route(route='/configure/router_settings')
        self.browser['wired_config_dynamic_dns_label'] = ddns_substring
        self.save_page()

    def get_mx_client_vpn_subnet(self):
        """Get the Client VPN subnet/cidr (string).

        Location: Security Appliance > Client VPN > Client VPN

        Sample HTML:
            <input autocomplete="new-password" id=
            "wired_config_client_vpn_subnet" name="wired_config[
            client_vpn_subnet]" size="20" type="text" value="10.0.0.0/24" />
        """
        self.browser.open_route(route='/configure/client_vpn_settings')
        return self.get_input_var_value(
            soup=self.browser.get_current_page(),
            var_id='wired_config_client_vpn_subnet',
        )

    def get_mx_client_vpn_dns_mode(self):
        """Get the Client VPN DNS mode (string).

        Location: Security Appliance > Client VPN > Client VPN

        Sample HTML:
            <select id="wired_config_client_vpn_dns_mode" name=
            "wired_config[client_vpn_dns_mode]"><option value="google_dns"
            selected="selected">Use Google Public DNS</option><option value=
            "opendns">Use OpenDNS</option><option value="custom">
            Specify nameservers...</option></select>
        """
        route = '/configure/client_vpn_settings'
        self.browser.open_route(route)
        return self.get_mx_dropdown_value(
            soup=self.browser.get_current_page(),
            var_id='wired_config_client_vpn_dns_mode',
        )

    def get_mx_custom_name_servers(self):
        """Returns a list of custom name servers.

        Location: Security Appliance > Client VPN > Client VPN

        Sample HTML:
            <textarea class="noresize" cols="20" id=
            "wired_config_client_vpn_dns" name="wired_config[client_vpn_dns]"
            rows="2">\n10.0.0.2\n10.0.0.3</textarea>
        """
        route = '/configure/client_vpn_settings'
        self.browser.open_route(route)
        return self.get_textarea_list(
            self.browser.get_current_page(),
            'wired_config_client_vpn_dns'
        )

    def get_mx_client_vpn_wins_enabled(self):
        """Returns a bool of whether Client VPN WINS is enabled.

        Location: Security Appliance > Client VPN > Client VPN

        Sample HTML:
            <select id="wired_config_client_vpn_wins_enabled" name=
            "wired_config[client_vpn_wins_enabled]"><option value="true">Specify
             WINS servers...</option><option value="false" selected="selected">
            No WINS servers</option></select>
        """
        self.browser.open_route(route='/configure/client_vpn_settings')
        dropdown_value = self.get_mx_dropdown_value(
            soup=self.browser.get_current_page(),
            var_id='wired_config_client_vpn_wins_enabled',
        )
        return dropdown_value == 'Enabled'

    def get_mx_client_vpn_secret(self):
        """Get Client VPN secret

        Location: Security Appliance > Client VPN > Client VPN

        Sample HTML for DDNS name:
            <input autocomplete="new-password" class="jsAnalyticsExclude"
            id="wired_config_client_vpn_secret" maxlength="32"
            name="wired_config[client_vpn_secret]" size="25"
            value="my-client-vpn-psk" type="password">
        """
        self.browser.open_route(route='/configure/router_settings')
        return self.get_input_var_value(
            soup=self.browser.get_current_page(),
            var_id='wired_config_client_vpn_secret',
        )

    def get_mx_client_auth_type(self):
        """Get the Client VPN authentication type

        Location: Security Appliance > Client VPN > Client VPN

        Sample HTML:
            select id="wired_config_client_vpn_auth_type"
                name="wired_config[client_vpn_auth_type]">
            <option value="meraki" selected="selected">Meraki cloud</option>
            <option value="radius">RADIUS</option>
            <option value="active_directory">Active Directory</option></select>
        """
        self.browser.open_route(route='/configure/router_settings')
        return self.get_mx_dropdown_value(
            soup=self.browser.get_current_page(),
            var_id='wired_config_client_vpn_auth_type',
        )

    def get_mx_sentry_vpn_enabled(self):
        """Return the bool of whether Sentry VPN is enabled

        Location: Security Appliance > Client VPN > Client VPN

        Sample HTML:
            <select id="wired_config_client_vpn_pcc_access_enabled" name=
            "wired_config[client_vpn_pcc_access_enabled]"><option value="true">
            Enabled</option><option value="false" selected="selected">
            Disabled</option></select>
        """
        self.browser.open_route(route='/configure/router_settings')
        dropdown_value = self.get_mx_dropdown_value(
            soup=self.browser.get_current_page(),
            var_id='wired_config_client_vpn_pcc_access_enabled',
        )
        return dropdown_value == 'Enabled'

    def get_mx_active_directory_enabled(self):
        """Return the bool of whether Active Directory auth is enabled.

        Location: Security Appliance > Active Directory

        Sample HTML:
            <select id="active_directory_enabled_select" name=
            "active_directory_enabled_select"><option value="true">Authenticate
            users with Active Directory</option><option value="false" selected=
            "selected">No authentication</option></select>
        """
        self.browser.open_route(route='/configure/active_directory')
        dropdown_value = self.get_mx_dropdown_value(
            soup=self.browser.get_current_page(),
            var_id='active_directory_enabled_select',
        )
        return dropdown_value == 'Authenticate users with Active Directory'

    def get_mx_primary_uplink(self):
        """Return the MX's primary uplink of ['WAN1', 'WAN2', 'Cellular']

        Location: Security Appliance > Traffic Shaping > Uplink selection

        Sample HTML:
            <select id="wired_config_primary_uplink" name=
            "wired_config[primary_uplink]" primary_uplink=
            "primary_uplink_select"><option value="0" selected="selected">WAN 1
            </option><option value="1">WAN 2</option></select>
        """
        self.browser.open_route(route='/configure/traffic_shaping')
        return self.get_mx_dropdown_value(
            soup=self.browser.get_current_page(),
            var_id='wired_config_primary_uplink',
        )

    def get_mx_amp_enabled(self):
        """Get the bool of whether AMP is enabled

        Location: Security Appliance > Threat Protection > AMP

        Sample HTML:
            <select id="scanning_enabled_select" name="scanning_enabled_select">
                <option value="true" selected="selected">Enabled</option>
                <option value="false">Disabled</option></select>
        """
        self.browser.open_route(route='/configure/security_filtering')
        dropdown_value = self.get_mx_dropdown_value(
            soup=self.browser.get_current_page(),
            var_id='wired_config_primary_uplink',
        )
        return dropdown_value == 'Enabled'

    def get_mx_ids_mode(self):
        """Return the ids mode of ['Disabled', 'Detection', 'Prevention']

        Location: Security Applaiance > Threat Protection > IDS/IPS

        Sample HTML:
            <select id="ids_mode_select" name="ids_mode_select">
                <option value="disabled" selected="selected">Disabled</option>
                <option value="detection">Detection</option>
                <option value="prevention">Prevention</option></select>
        """
        self.browser.open_route(route='/configure/security_filtering')
        return self.get_mx_dropdown_value(
            soup=self.browser.get_current_page(),
            var_id='ids_mode_select',
        )

    def get_mx_ids_ruleset(self):
        """Return the ids mode of ['Connectivity', 'Balanced', 'Security']

        Location: Security Applaiance > Threat Protection > IDS/IPS

        Sample HTML:
            <select id="ids_ruleset_select" name="ids_ruleset_select">
                <option value="high">Connectivity</option>
                <option value="medium" selected="selected">Balanced</option>
                <option value="low">Security</option></select>
        """
        # If IDS is disabled, don't send another value, even if it is the HTML
        if self.get_mx_ids_mode() == 'Disabled':
            return 'Disabled'

        self.browser.open_route(route='/configure/security_filtering')
        return self.get_mx_dropdown_value(
            soup=self.browser.get_current_page(),
            var_id='ids_ruleset_select',
        )

    @staticmethod
    def get_textarea_list(soup, var_id):
        """Return a list of values (split by \n) from a <textarea>."""
        textarea_list = soup.find("textarea", {'id': var_id}).text.split('\n')
        # Remove all '' elements. First element of this list will be ''
        # If there are no textarea elements, we would get ['', '', '']
        filtered_list = list(filter(None, textarea_list))
        return filtered_list

    @staticmethod
    def get_mx_dropdown_value(soup, var_id):
        """Get the value from variables starting with 'wired_config'

        Use when you see a dropdown in this HTML format:
        <select id="var-id" name="var-name">
            <option value="false"> -- Option#1 -- </option>
            ...
            <option value="true" selected="selected"> -- Option#2 -- </option>
        </select>

        Args:
            soup (BeautifulSoup): A soup object containing the HTML
            var_id (string): the id of a var, used to find its value
        Returns:
            (string): The text of the
        """
        dropdown = soup.find("select", {"id": var_id})
        dropdown_value = dropdown.find("option", selected=True).text
        return dropdown_value

    @staticmethod
    def get_input_var_value(soup, var_id):
        """Get the value from text input variables

        Use when you see this HTML format:
         <input id="wired_config_var" ... value="value">

        Args:
            soup (BeautifulSoup): A soup object containing the HTML
            var_id (string): the id of a var, used to find its value
        Returns:
            (string): The value of the variable
        """
        var_value = soup.find('input', {'id': var_id}).get('value')
        return var_value

    def save_page(self):
        """Click the 'Save' button after making a change."""
        print("Not implemented yet!", self.save_page())
