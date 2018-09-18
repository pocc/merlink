# -*- coding: utf-8 -*-
"""Utilities to scrape elements from / input text into an MX page.

Current functions:

mx_get_client_vpn_subnet,
mx_get_client_vpn_dns_mode,
mx_get_custom_name_servers,
mx_get_client_vpn_wins_enabled,
mx_get_client_vpn_secret,
mx_get_client_auth_type,
mx_get_sentry_vpn_enabled,
mx_get_active_directory_enabled,
mx_get_primary_uplink,
mx_get_amp_enabled,
mx_get_ids_mode,
mx_get_ids_ruleset
"""

from . import page_utils


def mx_get_client_vpn_subnet(self):
    """Get the Client VPN subnet/cidr (string).
    Location: Security appliance > Client VPN > Client VPN

    This value will exist regardless of whether Client VPN is enabled.

    Sample HTML:
        <input autocomplete="new-password" id=
        "wired_config_client_vpn_subnet" name="wired_config[
        client_vpn_subnet]" size="20" type="text" value="10.0.0.0/24" />
    """
    self.open_route('/configure/client_vpn_settings', "Security appliance")
    return page_utils.get_input_var_value(
        self.browser.get_current_page(),
        'wired_config_client_vpn_subnet')


def mx_get_client_vpn_dns_mode(self):
    """Get the Client VPN DNS mode (string).

    Location: Security appliance > Client VPN > Client VPN

    Sample HTML:
        <select id="wired_config_client_vpn_dns_mode" name=
        "wired_config[client_vpn_dns_mode]"><option value="google_dns"
        selected="selected">Use Google Public DNS</option><option value=
        "opendns">Use OpenDNS</option><option value="custom">
        Specify nameservers...</option></select>
    """
    route = '/configure/client_vpn_settings'
    self.open_route(route)
    return page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        'wired_config_client_vpn_dns_mode')


def mx_get_client_vpn_nameservers(self):
    r"""Return a list of custom name servers.

    Location: Security appliance > Client VPN > Client VPN

    Sample HTML:
        <textarea class="noresize" cols="20" id=
        "wired_config_client_vpn_dns" name="wired_config[client_vpn_dns]"
        rows="2">\n10.0.0.2\n10.0.0.3</textarea>
    """
    self.open_route('/configure/client_vpn_settings', "Security appliance")
    nameservers = page_utils.get_textarea_list(
        self.browser.get_current_page(),
        var_id='wired_config_client_vpn_dns')
    if nameservers == 'Specify nameservers...':
        nameservers = None
    return nameservers


def mx_get_client_vpn_wins_enabled(self):
    """Return a bool of whether Client VPN WINS is enabled.

    Location: Security appliance > Client VPN > Client VPN

    Sample HTML:
        <select id="wired_config_client_vpn_wins_enabled" name=
        "wired_config[client_vpn_wins_enabled]"><option value="true">
        Specify WINS servers...</option><option value="false"
        selected="selected">No WINS servers</option></select>
    """
    self.open_route('/configure/client_vpn_settings', "Security appliance")
    dropdown_value = page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        var_id='wired_config_client_vpn_wins_enabled')
    return dropdown_value == 'Enabled'


def mx_get_client_vpn_secret(self):
    """Get Client VPN secret.

    Location: Security appliance > Client VPN > Client VPN

    Sample HTML for DDNS name:
        <input autocomplete="new-password" class="jsAnalyticsExclude"
        id="wired_config_client_vpn_secret" maxlength="32"
        name="wired_config[client_vpn_secret]" size="25"
        value="my-client-vpn-psk" type="password">
    """
    self.open_route('/configure/client_vpn_settings', "Security appliance")
    return page_utils.get_input_var_value(
        self.browser.get_current_page(),
        var_id='wired_config_client_vpn_secret')


def mx_get_client_auth_type(self):
    """Get the Client VPN authentication type.

    Location: Security appliance > Client VPN > Client VPN

    Sample HTML:
        select id="wired_config_client_vpn_auth_type"
            name="wired_config[client_vpn_auth_type]">
        <option value="meraki" selected="selected">Meraki cloud</option>
        <option value="radius">RADIUS</option>
        <option value="active_directory">Active Directory</option></select>
    """
    self.open_route('/configure/client_vpn_settings', "Security appliance")
    return page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        var_id='wired_config_client_vpn_auth_type')


def mx_get_sentry_vpn_enabled(self):
    """Return the bool of whether Sentry VPN is enabled.

    Location: Security appliance > Client VPN > Client VPN

    Sample HTML:
        <select id="wired_config_client_vpn_pcc_access_enabled" name=
        "wired_config[client_vpn_pcc_access_enabled]"><option value="true">
        Enabled</option><option value="false" selected="selected">
        Disabled</option></select>
    """
    self.open_route('/configure/client_vpn_settings', "Security appliance")
    dropdown_value = page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        var_id='wired_config_client_vpn_pcc_access_enabled')
    return dropdown_value == 'Enabled'


def mx_get_active_directory_enabled(self):
    """Return the bool of whether Active Directory auth is enabled.

    Location: Security appliance > Active Directory

    Sample HTML:
        <select id="active_directory_enabled_select" name=
        "active_directory_enabled_select"><option value="true">Authenticate
        users with Active Directory</option><option value="false" selected=
        "selected">No authentication</option></select>
    """
    self.open_route('/configure/active_directory', "Security appliance")
    dropdown_value = page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        var_id='active_directory_enabled_select')
    return dropdown_value == 'Authenticate users with Active Directory'


def mx_get_primary_uplink(self):
    """Return the MX's primary uplink of ['WAN1', 'WAN2', 'Cellular'].

    Location: Security appliance > Traffic Shaping > Uplink selection

    Sample HTML:
        <select id="wired_config_primary_uplink" name=
        "wired_config[primary_uplink]" primary_uplink=
        "primary_uplink_select"><option value="0" selected="selected">WAN 1
        </option><option value="1">WAN 2</option></select>
    """
    self.open_route('/configure/traffic_shaping', "Security appliance")
    return page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        var_id='wired_config_primary_uplink')


def mx_get_amp_enabled(self):
    """Get the bool of whether AMP is enabled.
    # Should probably also check whether

    Location: Security appliance > Threat Protection > AMP

    Sample HTML:
        <select id="scanning_enabled_select"
        name="scanning_enabled_select">
            <option value="true" selected="selected">Enabled</option>
            <option value="false">Disabled</option></select>
    """
    self.open_route('/configure/security_filtering', "Security appliance")
    dropdown_value = page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        var_id='scanning_enabled_select')
    return dropdown_value == 'Enabled'


def mx_get_ids_mode(self):
    """Return the ids mode of ['Disabled', 'Detection', 'Prevention'].

    Location: Security Applaiance > Threat Protection > IDS/IPS

    Sample HTML:
        <select id="ids_mode_select" name="ids_mode_select">
            <option value="disabled" selected="selected">Disabled</option>
            <option value="detection">Detection</option>
            <option value="prevention">Prevention</option></select>
    """
    self.open_route('/configure/security_filtering', "Security appliance")
    return page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        var_id='ids_mode_select')


def mx_get_ids_ruleset(self):
    """Return the ids mode of ['Connectivity', 'Balanced', 'Security'].

    Location: Security Applaiance > Threat Protection > IDS/IPS

    Sample HTML:
        <select id="ids_ruleset_select" name="ids_ruleset_select">
            <option value="high">Connectivity</option>
            <option value="medium" selected="selected">Balanced</option>
            <option value="low">Security</option></select>
    """
    # If IDS is disabled, don't send another value, even if it is in the HTML
    if self.mx_get_ids_mode() == 'Disabled':
        return 'Disabled'

    self.open_route('/configure/security_filtering', "Security appliance")
    return page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        var_id='ids_ruleset_select')
