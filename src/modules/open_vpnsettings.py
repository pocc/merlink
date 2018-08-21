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

"""This will start the OS-dependent VPN settings window."""
from os import system
from sys import platform


def open_vpnsettings():
    """Opens OS-specific VPN settings."""
    if platform == 'win32':
        # Opens Windows 10 Settings > Network & Internet > VPN
        system('start ms-settings:network-vpn')
    elif platform == 'darwin':
        # Opens macOS System Settings > Network
        system('open /System/Library/PreferencePanes/Network.prefPane/')
    elif platform.startswith('linux'):  # covers vaild 'linux', 'linux2'
        # Opens System Settings > Network
        system('nm-connections-editor')
