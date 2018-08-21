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

"""After a failure to connect, this function will GUIfy the cause."""
from PyQt5.QtWidgets import QListWidgetItem, QListWidget
from PyQt5.QtGui import QIcon

# Local modules
from src.modules.pyinstaller_path_helper import resource_path


def tshoot_failed_vpn_dialog(has_passed_validation):
    """After a failure to connect, this function will GUIfy the cause.

    Args:
        has_passed_validation (list(bool)): A list of bools corresponding
        to the success of 6 tests validating against common misconfigurations.

    Returns:
        (QListWidget): A QListWidget that has checkmark/X icons and
        accompanying text according to whether that text's test passed.
    """

    validation_list = QListWidget()
    validation_textlist = [
        "Is the MX online?",
        "Can the client ping the firewall's public IP?",
        "Is the user behind the firewall?",
        "Is Client VPN enabled?",
        "Is authentication type Meraki Auth?",
        "Are UDP ports 500/4500 port forwarded through firewall?"]
    # "Is the user authorized for Client VPN?",
    # For as many times as items in the validation_textlist
    for i in range(len(validation_textlist)):
        # Initialize a QListWidgetItem out of a string
        item = QListWidgetItem(validation_textlist[i])
        validation_list.addItem(item)  # Add the item to the QListView

    for i in range(len(validation_textlist)):
        print("has passed" + str(i) + str(has_passed_validation[i]))
        if has_passed_validation[i]:
            validation_list.item(i).setIcon(
                QIcon(resource_path('src/media/checkmark-16.png')))
        else:
            validation_list.item(i).setIcon(
                QIcon(resource_path('src/media/x-mark-16.png')))

    return validation_list
