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
"""Utilities to scrape elements from / input text into an MS page.

This module is half-implemented for demonstration purposes.
"""

from . import page_utils


def ms_get_management_vlan(self):
    """Return the management vlan.

    Location: Switches > Switch Settings > VLAN Configuration

    Sample HTML:
        <input id="node_group_management_vlan" name=
        "node_group[management_vlan]" type="text" value="1">

    Returns:
        (string): The management VLAN for this switch network.

    """
    self.open_route('/configure/switch_settings', redirect_ok=True)
    textarea_values = page_utils.get_textarea_list(
        self.browser.get_current_page(),
        var_id='node_group_management_vlan')
    return textarea_values[0]


def ms_get_rstp_enabled(self):
    """Return the bool of whether RSTP is enabled.

    Location: Switches > Switch Settings > VLAN Configuration

    Sample HTML:
        <select id="node_group_use_stp" name="node_group[use_stp]">
            <option value="true" selected="selected">Enable RSTP</option>
            <option value="false">Disable RSTP</option></select>

    Returns:
        (bool): Whether RSTP is enabled for this switch network.

    """
    self.browser.open_route('/configure/switch_settings', redirect_ok=True)
    dropdown_value = page_utils.get_textarea_list(
        self.browser.get_current_page,
        var_id='node_group_use_stp')
    return dropdown_value == 'Enable RSTP'
