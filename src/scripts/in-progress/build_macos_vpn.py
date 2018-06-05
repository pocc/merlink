#!/usr/bin/python3
"""
ABOUT
-----
* This file will build a VPN by adding XML to /Library/Preferences/SystemConfiguration/preferences.plist
* There are 3 value sets that need to be inserted into preferences.plist to add a VPN connection
* Once a VPN connection has formed, we can use the BSD utilities scutil --nc and networksetup to monitor the VPN

VARS
----
* variables in blob: $GUID, $Username, $FirewallIp, $VpnName, $SETID
* $SETID will be set by system (it's unknown but it's value doesn't matter)
* $SETID is a location in the location list in Network Settings
"""

import xml.etree.ElementTree as ET
import os

os.system('cp /Library/Preferences/SystemConfiguration/preferences.plist')

current_vpn_prefs = ET.parse('/Library/Preferences/SystemConfiguration/preferences.plist')


