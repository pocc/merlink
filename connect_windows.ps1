# Windows Powershell
# Given an MX public IP, username and password, use powershell to create  a VPN connection

# Add the VPN connection
Add-VpnConnection -name $vpn_name -ServerAddress $mx_ip
# Add required settings for Meraki VPN
Set-VpnConnection -name $vpn_name -ServerAddress $mx_ip -AuthenticationMethod PAP -L2tpPsk $psk -TunnelType L2tp `
-RememberCredential $False -Force -WarningAction SilentlyContinue
# rasdial connects a VPN (and is really old - it connects using a phonebook!)
rasdial $vpn_name $username $password