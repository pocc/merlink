# -*- coding: utf-8 -*-
"""These functions fetch or parsre JSON blobs from dashboard."""
import re
import json
import mechanicalsoup
import requests


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
    self.browser.open(administered_orgs_url)

    cookiejar = self.browser.get_cookiejar()
    response = requests.get(administered_orgs_url, cookies=cookiejar)
    administered_orgs = json.loads(response.text)
    if self.is_network_admin:
        self.org_qty = len(self.orgs_dict)

    return administered_orgs


def get_page_links(self):
    """Get all page links from current page's pagetext."""
    pagetext = self.browser.get_current_page().text
    json_text = re.findall(
        r'window\.initializeSideNavigation\([ -(*-~\r\n]*\)',
        pagetext)[0][69:-10]
    json_dict = json.loads(json_text)
    # Format of this dict: {tab_menu: {tab: {'url': val, 'name': val}, ...
    page_url_dict = {}
    for tab_menu in range(len(json_dict['tab_menu']['tabs'])):
        tab_menu = json_dict['tab_menu']['tabs'][tab_menu]
        category = tab_menu['name']
        page_url_dict[category] = {}
        for menu in ('Monitor', 'Configure'):
            # Cameras do not have a configure section.
            if not (category == 'Cameras' and menu == 'Configure'):
                menu_items = tab_menu['menus'][menu]['items']
                for tab_index, _ in enumerate(menu_items):
                    # Sometimes a tab JSON is Null, in which case skip it.
                    if menu_items[tab_index]:
                        name = menu_items[tab_index]['name']
                        url = menu_items[tab_index]['url']
                        page_url_dict[category][name] = url

    return page_url_dict


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


def open_route(self, target_route, category=None):
    """Redirect the browser to a page, given its route.

    Each page in dashboard has a route. If we're already at the page we
    need to be at to scrape, don't use the browser to open a page.

    Args:
        target_route (string): Text following '/manage' in the url that
            identifies (and routes to) a page.
        category (bool): Redirect to correct network. For example,
            open_route('/configure/vpn_settings') is used on the switch
            subnetwork of a combined network that has a firewall. In this
            scenario, redirect to the firewall's page.
    """
    if category:
        target_url = self.combined_network_redirect(target_route, category)
        if not target_url:
            raise LookupError
    else:
        current_url = self.browser.get_url()
        network_partial, _ = current_url.split('/manage')
        network_base, _ = network_partial.split('.com/')
        network_name = self.orgs_dict[self.active_org_id]['node_groups'][
            self.active_network_id]['t']
        eid = self.orgs_dict[self.active_org_id]['node_groups'][
            self.active_network_id]['eid']
        target_url = network_base + '.com/' + network_name + '/n/' + eid + \
            '/manage' + target_route

    # Don't go to where we already are or have been!
    has_pagetext = [i for i in self.pagetexts.keys() if target_route in i]
    if self.url() != target_url and not has_pagetext:
        try:
            self.browser.open(target_url)
            self.pagetexts[target_url] = self.browser.get_current_page()
            opened_url = self.browser.get_url()
            has_been_redirected = opened_url != target_url
            if has_been_redirected:
                handle_redirects(target_url, opened_url)
        except mechanicalsoup.utils.LinkNotFoundError as error:
            print('Attempting to open', self.url(), 'with route',
                  target_route, 'and failed.', error)


def combined_network_redirect(self, route, category):
    """Redirect to a different network type in a combined network."""
    pagelink_dict = self.get_page_links()
    for page in pagelink_dict[category]:
        page_url = pagelink_dict[category][page]
        if route in page_url:
            return page_url


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
