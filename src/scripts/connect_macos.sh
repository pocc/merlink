#!/bin/bash
# This script takes 1 parameter - the name of a VPN connection that has already been created
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

