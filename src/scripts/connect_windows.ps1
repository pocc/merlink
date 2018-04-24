# Windows Powershell
# Given vpn name, PSK, DDNS, public IP, username and password, use powershell to create  a VPN connection

# Set the local variables to external parameters
$vpn_name = $args[0]
$psk = $args[1]
$ddns = $args[2]
$mx_ip = $args[3]
$username = $args[4]
$password = $args[5]
$is_split_tunnel = $args[6]
$DEBUG = $args[7]

# While debugging, following command will print all variables
if ($DEBUG -eq 'True') {
    invoke-expression 'write-host "Debugging ~ vpn_name:" $vpn_name "| psk:" $psk "| ddns:" $ddns "| mx_ip:" $mx_ip "| username:" $username "| password:" $password "| split_tunnel:" $is_split_tunnel'
}

# Disconnect from any other VPNs first
foreach ($connection in Get-VpnConnection) {
    if (($connection | select -ExpandProperty ConnectionStatus) -eq 'Connected') {
        $vpn_name = $connection | select -ExpandProperty Name
        rasdial $vpn_name /Disconnect
    }
}

# Add the VPN connection if it doesn't already exist, prevent add-vpnconnection from complaining about it
$ErrorActionPreference = 'silentlycontinue'
Add-VpnConnection -name $vpn_name -ServerAddress '0'
$ErrorActionPreference = 'Continue'

# Add required settings for Meraki VPN
Set-VpnConnection -name $vpn_name -ServerAddress $mx_ip -AuthenticationMethod PAP -L2tpPsk $psk -TunnelType L2tp `
-RememberCredential $False -SplitTunneling $is_split_tunnel -Force -WarningAction SilentlyContinue
# rasdial connects a VPN (and is really old - it connects using a phonebook!)
$result = rasdial $vpn_name $username $password

write-host $result
# If we are successfully or already connected, return success, otherwise failure
if (($result -match 'Successfully connected') -Or ($result -match 'already connected')) {
    Write-host "Connection success!"
    $EXIT_CODE=0
} else {
    Write-host "Connection failed!"
    $EXIT_CODE=1
}

return $EXIT_CODE