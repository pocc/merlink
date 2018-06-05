#!/bin/bash
# Generate a random UUID. 
vpnUuid=$(uuidgen)
echo $vpnUuid

# The name of connection type displayed in GUI
connectionName=$1
# IP address of server
serverAddress=$2
# L2TP PSK
sharedSecret=$3
# L2TP username
username=$4
# L2TP password
password=$5


# Setup Keychain shared secret granting appropriate access for the OS apps
# To troubleshoot use the following command:
# security dump-keychain -a /Library/Keychains/System.keychain
# Files that should have access to this PSK keychain can be found
# by searching for your connection's name in the output
# First 7 are required, giving access to scutil allows us to connect/disconnect
authorized_files="-T /usr/libexec/nehelper -T /System/Library/Frameworks/NetworkExtension.framework/PlugIns/NEIKEv2Provider.appex -T /usr/libexec/nesessionmanager -T /usr/libexec/neagent -T /usr/sbin/racoon -T /usr/sbin/pppd -T /System/Library/PreferencePanes/Network.prefPane/Contents/XPCServices/com.apple.preference.network.remoteservice.xpc -T /System/Library/Frameworks/SystemConfiguration.framework/Versions/A/Helpers/SCHelper -T /usr/sbin/scutil"

# Use the security command to add the IPSec Shared Secret and give authorized_files appropriate access
# /Library/Keychains/System.keychain is required at the end
/usr/bin/security add-generic-password -a com.apple.ppp.l2tp -s $vpnUuid.SS -l "$connectionName" -D "IPSec Shared Secret" -w "$sharedSecret" $authorized_files -U /Library/Keychains/System.keychain
/usr/bin/security add-generic-password -a "$username" -s "$vpnUuid" -l "$connectionName" -D "VPN Password" -w "$password" $authorized_files -U /Library/Keychains/System.keychain


# Add entries to preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:DNS dict" /Library/Preferences/SystemConfiguration/preferences.plist

/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:IPSec:AuthenticationMethod string SharedSecret" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:IPSec:SharedSecret string $vpnUuid\.SS" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:IPSec:SharedSecretEncryption string Keychain" /Library/Preferences/SystemConfiguration/preferences.plist

/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:IPv4:ConfigMethod string PPP" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:IPv4:OverridePrimary integer 1" /Library/Preferences/SystemConfiguration/preferences.plist

/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:IPv6:ConfigMethod string Automatic" /Library/Preferences/SystemConfiguration/preferences.plist

/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:Interface:SubType string L2TP" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:Interface:Type string PPP" /Library/Preferences/SystemConfiguration/preferences.plist

/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:ACSPEnabled string 1" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:AuthName string $username" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:AuthPassword string $vpnUuid" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:AuthPasswordEncryption string Keychain" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:CommDisplayTerminalWindow integer 0" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:CommRedialCount integer 1" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:CommRedialEnabled integer 0" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:CommRedialInterval integer 5" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:CommRemoteAddress string $serverAddress" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:CommUseTerminalScript integer 0" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:DialOnDemand integer 0" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:DisconnectOnFastUserSwitch integer 1" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:DisconnectOnIdleTimer integer 600" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:DisconnectOnLogout integer 1" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:DisconnectOnSleep integer 0" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:IPCPCompressionVJ integer 0" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:IdleReminder integer 0" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:IdleReminderTimer integer 1800" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:LCPEchoEnabled integer 1" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:LCPEchoFailure integer 15" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:LCPEchoInterval integer 20" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:logfile string /var/log/ppp.log" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:PPP:VerboseLogging integer 0" /Library/Preferences/SystemConfiguration/preferences.plist

/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:Proxies:FTPPassive integer 1" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:SMB dict" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :NetworkServices:$vpnUuid:UserDefinedName string $connectionName" /Library/Preferences/SystemConfiguration/preferences.plist

# Get first network location and find its UUID (default is 'Automatic')
locationUuid=`/usr/libexec/Plistbuddy -c "Print :Sets" /Library/Preferences/SystemConfiguration/preferences.plist | grep -B1 -m1 $(networksetup -listlocations) | grep Dict | awk '{ print $1 }'`
	
# Add new config to first location set
/usr/libexec/PlistBuddy -c "Add :Sets:$locationUuid:Network:Service:$vpnUuid dict" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :Sets:$locationUuid:Network:Service:$vpnUuid:__LINK__ string \/NetworkServices\/$vpnUuid" /Library/Preferences/SystemConfiguration/preferences.plist
/usr/libexec/PlistBuddy -c "Add :Sets:$locationUuid:Network:Global:IPv4:ServiceOrder: string $vpnUuid" /Library/Preferences/SystemConfiguration/preferences.plist
