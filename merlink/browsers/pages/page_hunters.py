# -*- coding: utf-8 -*-
"""These functions fetch or parse text from Dashboard page HTML."""
import re
import json


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
