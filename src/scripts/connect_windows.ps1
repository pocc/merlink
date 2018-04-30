# Windows Powershell
# Given VPN name, PSK, DDNS, public IP, username and password, use powershell to create  a VPN connection

##### ADDITIONAL SET-VPNCONNECTION PARAMETERS THAT ARE NOT BEING USED #####
# Items that have been added to this script have a '+++'

### Switch paramaters (doesn't take an argument) ###
# -AllUserConnection : All users on the PC have access to this VPN connection | Flag with no value required
# -AsJob (we can make this option available, but it shouldn't actually do anything
# -PassThru (we can make this optino available, but it shouldn't actually do anything

### CimSession ###
# -CimSession : Runs the cmdlet in a remote session or on a remote computer.

### CimInstance ###
# -ServerList : CimInstance Array of servers that can be connected to

### String ###
# +++ -Name : Name of the VPN connection
# +++ -ServerAddress : Address of the Server
# +++ -AuthenticationMethod : Authentication Type. For Meraki FWs, this is PAP
# +++ -TunnelType : Type of the tunnel. For Meraki FWs, this is L2TP
# +++ -L2tpPsk : Pre-Shared Key for L2TP
# -DnsSuffix : contoso.com for server.contoso.com
# -IdleDisconnectSeconds : seconds after which connection will die
# -UseWinlogonCredential : Use your windows login credentials

### $True/$False is passed in as string parameter ###
# +++ -SplitTunneling : Go to the internet via your local connection instead of through the remote FW
# +++ -RememberCredential : Save the credential so you don't have to reenter

### 3rd party parameters (may be useful later) ###
# -CustomConfiguration : Requires XML file but will pass parametrs to set-vpnconnection
# -PlugInApplicationID : Specifies the identifier for a third party application.
# -ThirdPartyVpn :  Indicates that the cmdlet runs for a third party profile.

### Extra options that will not likely be used ###
# -MachineCertificateEKUFilter
# -MachineCertificateIssuerFilter
# -ThrottleLimit
# -EapConfigXmlStream
# -Confirm
# -WhatIf


# Note that there is no limit on # of powershell ags, but around ~8192 characters on 64bit is a limit
# Set the local variables to external parameters (all are coming in as string)
$vpn_name = $args[0]                    # String
$psk = $args[1]                         # String
$ddns = $args[2]                        # String
$mx_ip = $args[3]                       # String
$username = $args[4]                    # String
$password = $args[5]                    # String
$DnsSuffix = $args[6]                   # String
$IdleDisconnectSeconds = [int]$args[7]  # Integer (of seconds), converting to int
$DEBUG = $args[8]                       # If DEBUG var is set in python
$is_split_tunnel = [int]$args[9]        # 0/1 (String), converting to int
$has_remember_credential=[int]$args[10] # 0/1 (String), converting to int
$UseWinlogonCredential = [int]$args[11] # 0/1 (String), converting to int

# While debugging, following command will print all variables
write-host "These are the parameters that powershell received:"
for ($i=0; $i -lt 12; $i++) {write-host "$i th parameter is $($args[$i])"}

# Disconnect from any active VPNs first
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
 -RememberCredential $has_remember_credential `
-SplitTunneling $is_split_tunnel -UseWinlogonCredential $UseWinlogonCredential `
-Force -WarningAction SilentlyContinue

# Only set these variables if the user has set them
if ($DnsSuffix -ne '-') {  # In python script, '-' is default
    Set-VpnConnection -name $vpn_name -DnsSuffix $DnsSuffix
}

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