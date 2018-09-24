# -*- coding: utf-8 -*-
"""Utilities to scrape elements from / input text into a page."""


def get_textarea_list(soup, var_id):
    r"""Return a list of values (split by \\n) from a <textarea>.

    Args:
        soup (soup): soup pagetext that will be searched.
        var_id (string): the id of a var, used to find its value
    Returns:
        (string): The list of values from a textarea.

    """
    try:
        textarea_list = soup.find("textarea", {'id': var_id}).text.split('\n')
        # Remove all '' elements. First element of this list will be ''
        # If there are no textarea elements, we would get ['', '', '']
        filtered_list = list(filter(None, textarea_list))
        return filtered_list
    except AttributeError:
        print('\nERROR:  <' + var_id + '>  not found!\nPagesoup:\n\n', soup)
        raise LookupError


def get_dropdown_value(soup, var_id):
    """Get the current value from a dropdown list.

    Use when you see a dropdown in this HTML format:
    <select id="var-id" name="var-name">
        <option value="false"> -- Option#1 -- </option>
        ...
        <option value="true" selected="selected"> -- Option#2 -- </option>
    </select>

    Args:
        soup (soup): soup pagetext that will be searched.
        var_id (string): the id of a var, used to find its value.
    Returns:
        (string): The text of the dropdown value.

    """
    try:
        dropdown = soup.find("select", {"id": var_id})
        dropdown_value = dropdown.find("option").text
        return dropdown_value
    except AttributeError:
        print('\nERROR:  <' + var_id + '>  not found!\nPagesoup:\n\n', soup)
        raise LookupError


def get_all_dropdown_values(soup, var_id):
    """Get all values from a dropdown list.

    See .get_dropdown_value for HTML example.

    Args:
        soup (soup): soup pagetext that will be searched.
        var_id (string): the id of a var, used to find its value.
    Returns:
        (list(string)): A list of dropdown values.

    """
    try:
        dropdown = soup.find("select", {"id": var_id})
        dropdown_values = []
        for bs4_tag in dropdown.find_all("option"):
            dropdown_values.append(bs4_tag.text)
        return dropdown_values
    except AttributeError:
        print('\nERROR:  <' + var_id + '>  not found!\nPagesoup:\n\n', soup)
        raise LookupError


def get_input_var_value(soup, var_id):
    """Get the value from text input variables.

    Use when you see this HTML format:
     <input id="wired_config_var" ... value="value">

    Args:
        soup (soup): soup pagetext that will be searched.
        var_id (string): The id of a var, used to find its value.
    Returns:
        (string): The value of the variable

    """
    try:
        var_value = soup.find('input', {'id': var_id}).get('value')
        return var_value
    except AttributeError:
        print('\nERROR:  <' + var_id + '>  not found!\nPagesoup:\n\n', soup)
        raise LookupError


def save_page(browser):
    """Click the 'Save' button after making a change.
    Args:
        browser (DashboardBrowser): Session to save settings with.

    """
    print("Not implemented yet!", browser.browser.get_url())
