#!/bin/bash
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


# This script the name of a VPN connection that has already been created
/usr/sbin/networksetup -connectpppoeservice "$1"

# Keeping this as backup in case Apple breaks networksetup
# Applescript that will work provided you are using script editor
# TODO: Figure out how to pass variables from bash to applescript

# osascript -e '
# tell application "System Events"
#	tell current location of network preferences
#		set VPN to service $vpnName
#		if exists VPN then connect VPN
#	end tell
# end tell'

