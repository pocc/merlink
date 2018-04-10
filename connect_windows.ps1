# Windows Powershell
# Given DDNS, public IP, username and password, use powershell to create  a VPN connection

# Set the local variables to external parameters
$ddns = $args[0]
$mx_ip = $args[1]
$username = $args[2]
$password = $args[3]

# Add the VPN connection
Add-VpnConnection -name $vpn_name -ServerAddress $mx_ip
# Add required settings for Meraki VPN
Set-VpnConnection -name $vpn_name -ServerAddress $mx_ip -AuthenticationMethod PAP -L2tpPsk $psk -TunnelType L2tp `
-RememberCredential $False -Force -WarningAction SilentlyContinue
# rasdial connects a VPN (and is really old - it connects using a phonebook!)
rasdial $vpn_name $username $password

# Code for returning a value
$connection_success = 1
if ($connection_success) {
    Write-host "Connection success!"
    $LASTEXITCODE=1
    }
else {
    Write-host "Connection failed!"
    $LASTEXITCODE=0
}
