#!/bin/bash
# This bash file will create and connect an L2TP VPN connection on linux

# Verify that we have required packages
# Verify that we have network-manager
if [ $(which nmcli) != '/usr/bin/nmcli' ]; then
    echo "ERROR: nmcli is not installed!"
    echo "Please install Network Manager (https://wiki.gnome.org/Projects/NetworkManager)"
    sleep 5
    exit 1
fi

# Each OS will have a <OS type>-release file in /etc
# Checking for deb and rpm because they come as prebuilt packages
# https://github.com/nm-l2tp/network-manager-l2tp/wiki/Prebuilt-Packages
# deb-based systems
# TODO see if presence of this file is cleaner indicator of l2tp plugin: /etc/NetworkManager/VPN/nm-l2tp-service.name
if [ -f /etc/debian_version ] && [[ -z $(dpkg -l network-manager-l2tp 2>/dev/null) ]]; then
	echo "ERROR: network-manager-l2tp must be installed on this debian-based system"
	sleep 5
	exit 2
# rpm-based systems
elif [ -f /etc/redhat-release ] && [[ -z $(rpm -qa NetworkManager-l2tp 2>/dev/null) ]]; then
	echo "ERROR: NetworkManager-l2tp must be installed on this redhat-based system"
	sleep 5
	exit 3
fi

# Linux Mint doesn't come with strongswan-plugin-openssl, which is required. Error out if
if [ $(cat /etc/os-release | grep Mint) ] && [[ -z $(dpkg -l strongswan-plugin-agent) ]]; then
	echo "ERROR: strongswan-plugin-openssl must be installed. Exiting..."
	sleep 5
	exit 4
fi

# If there are too few arguments, exit
if [[ -z $1 ]] || [[ -z $2 ]] || [[ -z $3 ]] || [[ -z $4 ]] || [[ -z $5 ]] ; then
    echo "Incorrect number of arguments, expecting 5"
    echo "Correct usage:\n  linux-vpn.sh 'MyVpnName' 'MyServerAddress' 'MyPsk' 'MyUsername' 'MyPassword'"
    sleep 5
    exit 5
fi

# Set variables from params
# Remove special characters [`!$'" ]. vpn_name has max of 15 chars, so cut off vpn_name if longer.
vpn_name="$(echo $1 | sed 's/[\`\!\$\/'\''\"\ ]//g' | cut -c1-15)"
echo 'vpn_name: '${vpn_name}
# If the vpn_name is now empty due to these removals, name it l2tp
if [[ -z vpn_name ]]; then vpn_name='l2tp'; fi
firewall_ip=$2
psk=$3
username=$4
password=$5

# Generate NetworkManager VPN connection
# l2tp gets stored as type org.freedesktop.NetworkManager.l2tp
nmcli con add type vpn ifname ${vpn_name} vpn-type l2tp
# nmcli prepends with 'vpn-', so we should too
vpn_name=vpn-${vpn_name}


# Overwrite config created at /etc/NetworkManager/system-connections/$vpn_name
# This content has been lifted from a successful connection
cat <<EOT > /etc/NetworkManager/system-connections/${vpn_name}
[connection]
id=${vpn_name}
# Create a UUID for this connection
uuid=$(uuidgen)
type=vpn
autoconnect=false
# Get current user and give them permission to this VPN
permissions=user:$(who | awk '{print $1;}'):;

[vpn]
gateway=${firewall_ip}
ipsec-enabled=yes
ipsec-esp=3des-sha1
ipsec-forceencaps=yes
ipsec-ike=3des-sha1-modp1024
ipsec-psk=${psk}
password-flags=0
user=${username}
mru=1500
mtu=1500
service-type=org.freedesktop.NetworkManager.l2tp

[vpn-secrets]
password=${password}

[ipv4]
dns-search=
method=auto

[ipv6]
addr-gen-mode=stable-privacy
dns-search=
ip6-privacy=0
method=auto
EOT


# Reload the connections
sudo nmcli con reload
# REQUIRED for network-manager-l2tpd to work (see description 
# for https://launchpad.net/~seriy-pr/+archive/ubuntu/network-manager-l2tp)
sudo service xl2tpd stop
sudo systemctl disable xl2tpd 2>/dev/null

# Connect
# NOTE: If you start or enable either of these at any point, the connection will fail
sudo nmcli con up id ${vpn_name}

# Disconnect
#sudo nmcli con down id $vpn_name
