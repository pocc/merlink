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
"""Utilities that make permanent changes to your organization

DO NOT USE THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING! YOU HAVE BEEN WARNED.

All functions that make a reversible change should start with 'change'.
All functions that make a potentially breaking change start with 'break'.
Helper functions should start with 'do'.
"""
import re

import requests

from .page_hunters import get_pagetext_mkiconf


def break_onetime_tfa_codes(self):
    """Reset the TFA codes and print the list of new ones.

    Go to /users/edit and commit for this HTML to generate new codes:
    HTML:
        <input name="commit" type="submit"
        value="Generate a new set of one-time codes">
    """
    self.open_route('/users/edit?only_path=false&protocol=https')
    base_url = self.get_url().split('/manage')[0] + '/manage'
    url = base_url + '/users/sms_auth_one_time_codes'
    params = {'generate': 'true', 'return_page': 'edit'}
    commit_msg = '&commit=Generate+a+new+set+of+one-time+codes'
    self.push_button(url, params, commit_msg)

    url = url.split('/manage')[0] + '/manage/users/edit'
    response = requests.get(url=url,
                            json=self.request_body,
                            headers=self.header_dict)
    if 'New one-time codes generated.' in response.text:
        print('Successfully generated new codes!')
    new_onetime_codes = re.findall('(?<=<li>)(\d{6})(?=<\/li>)',
                                   response.text)
    print(new_onetime_codes)


def do_push_button(self, url, params, commit, req_body_params=None):
    """Push a button by following its url

    Args:
        self: Required for getting a cookiejar and pagetext.
        url (string): Target route that pushing the button would trigger.
        params (dict): Request queries that go after the url.
        commit (string): Name of the button (i.e. value in HTML).
        req_body_params (dict): Dict of other vars to be
            added to the request body.
    """
    from urllib.parse import urlencode
    cookie_string = ''
    cookie_dict = dict(self.browser.browser.get_cookiejar())
    for key in cookie_dict:
        if key != 'dash_auth':
            cookie_string += urlencode({key: cookie_dict[key]}) + '; '

    cookie_string += 'dash_auth=' + cookie_dict['dash_auth']
    # Commit message cannot be url-encoded.
    encoding = 'utf8=%E2%9C%93&'
    mkiconf_vars = get_pagetext_mkiconf(self.browser.get_page().text)
    authenticity_token = urlencode({
        'authenticity_token': mkiconf_vars['authenticity_token']})

    more_params = ''
    if req_body_params:
        more_params = '&' + urlencode(req_body_params)
    request_body = encoding + authenticity_token + commit + more_params
    header_dict = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookie_string,
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
    }
    requests.request('POST', url=url, json=request_body,
                     headers=header_dict, params=params)
    self.request_body = request_body
    self.header_dict = header_dict


def do_save_page(browser):
    """Click the 'Save' button after making a change.
    Args:
        browser (DashboardBrowser): Session to save settings with.

    """
    print("Not implemented yet!", browser.browser.get_url())