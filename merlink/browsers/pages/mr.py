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
"""Utilities to scrape elements from / input text into an MR page.

This module is half-implemented for demonstration purposes.
"""

from . import page_utils


def mr_get_ssids(self):
    """Return a list of ssids.

    Location: Wireless > Access Control > Access Control

    Sample HTML:
        <select class="nosave notrack" id="select_ssid" name="select[ssid]"
        notranslate="">
            <option value="0" selected="&quot;selected&quot;">
            Bill Wi the Science Fi</option>
            ...
            <option value="14">...</option>
       </select>

    Returns:
        (list(string)): A list of SSIDs.

    """
    self.open_route('/configure/access_control', "Wireless")
    dropdown_values = page_utils.get_all_dropdown_values(
        self.browser.get_current_page(),
        var_id='select_ssid')
    return dropdown_values


def mr_get_group_policies_by_device_type_enabled(self):
    """Return a bool of whether group policies by device type is enabled.

    Location: Wireless > Access Control > Assign group policies by device type

    Sample HTML for Auto group policies enabled:
        <select id="ssid_auto_group_policies_enabled" name=
        "ssid[auto_group_policies_enabled]">
        <option value="false">Disabled: do not assign group policies
            automatically</option>
        <option value="true">Enabled: assign group policies
            automatically by device type</option></select>

    Returns:
        (list(string)): A list of SSIDs.
    """
    self.open_route('/configure/access_control', "Wireless")
    dropdown_value = page_utils.get_dropdown_value(
        self.browser.get_current_page(),
        var_id='ssid_auto_group_policies_enabled')
    enabled_str = 'Enabled: assign group policies automatically by device type'
    return dropdown_value == enabled_str
