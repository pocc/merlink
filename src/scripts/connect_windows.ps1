# Windows Powershell
# Given vpn name, PSK, DDNS, public IP, username and password, use powershell to create  a VPN connection

##### ADDITIONAL SET-VPNCONNECTION PARAMETERS THAT ARE NOT BEING USED #####

### Switch paramaters ###
# -AllUserConnection : All users on the PC have access to this VPN connection | Flag with no value required
# -AsJob (we can make this option available, but it shouldn't actually do anything
# -PassThru (we can make this optino available, but it shouldn't actually do anything

### CimSession ###
# -CimSession : Runs the cmdlet in a remote session or on a remote computer.

### String (more) ###
# -DnsSuffix : contoso.com for server.contoso.com
# -IdleDisconnectSeconds : sec after which connection will die
# -RememberCredential : Save the credential so you don't have to reenter (true/false as string)
# -ServerList : Array of servers that can be connected to
# -UseWinlogonCredential : Use your widows login

### 3rd party parameters (may be useful later) ###
# -CustomConfiguration : Requires XML file but will pass parametrs to set-vpnconnection
# -PlugInApplicationID : Specifies the identifier for a third party application.
# -ThirdPartyVpn :  Indicates that the cmdlet runs for a third party profile.

### Extra options that may be irrelevant ###
# -MachineCertificateEKUFilter
# -MachineCertificateIssuerFilter
# -ThrottleLimit
# -EapConfigXmlStream
# -Confirm
# -WhatIf


# Note that there is no limit on # of powershell ags, but around ~8192 characters on 64bit is a limit
# Set the local variables to external parameters (all are coming in as string)
$vpn_name = $args[0]    # String
$psk = $args[1]                 # String
$ddns = $args[2]                # String
$mx_ip = $args[3]               # String
$username = $args[4]            # String
$password = $args[5]            # String
$split_tunnel_arg = $args[6]    # True/False (String)
$DEBUG = $args[7]

# While debugging, following command will print all variables
if ($DEBUG -eq 'True') {
    invoke-expression 'write-host "Debugging ~ vpn_name:" $vpn_name "| psk:" $psk "| ddns:" $ddns "| mx_ip:" $mx_ip "| username:" $username "| password:" $password "| split_tunnel:" $is_split_tunnel'
}

# Manually assign boolean true for string true so we don't have to deal with it in parameter passing
if ($split_tunnel_arg -eq 'True'){
    $is_split_tunnel = $True
}
else {$is_split_tunnel = $False}

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