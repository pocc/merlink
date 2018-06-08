#!/bin/bash
# This bash file will create and connect an L2TP VPN connection on linux

# Verify that required nmcli (and by extension, network manager) is installed
if [ -z $(which nmcli) ]; then
    echo "ERROR: nmcli is not installed!"
    echo "Please install Network Manager (https://wiki.gnome.org/Projects/NetworkManager)"
    exit 1 # Exit with nmcli failure   
fi
if [ -z $1 ] || [ -z $2 ] || [ -z $3 ] || [ -z $4 ] || [ -z $5 ] ; then
    echo "Incorrect number of arguments, expecting 5"
    echo "Correct usage:\n  linux-vpn.sh 'MyVpnName' 'MyFirewallIp' 'MyPsk' 'MyUsername' 'MyPassword'"
    exit 3 # Exit due to too few args
fi


if [ -z $(which git) ]; then
    sudo apt-get install -y git
fi


# If network-manager-l2tp is missing, install it
dpkg_l2tp=$(sudo dpkg -l network-manager-l2tp 2>&1)
if [[ $dpkg_l2tp = *"no packages found matching"* ]] ; then
    sudo add-apt-repository ppa:nm-l2tp/network-manager-l2tp -y
    sudo apt-get update
    sudo apt-get install -y network-manager-l2tp network-manager-l2tp-gnome
fi

# Set variables from params
vpn_name=$1
firewall_ip=$2
psk=$3
username=$4
password=$5

# Generate NetworkManager VPN connection
# l2tp gets stored as type org.freedesktop.NetworkManager.l2tp
nmcli con add type vpn ifname $vpn_name vpn-type l2tp
# nmcli prepends with 'vpn-', so we should too
vpn_name=vpn-$vpn_name


# Overwrite config created at /etc/NetworkManager/system-connections/$vpn_name
# This content has been lifted from a successful connection
cat <<EOT > /etc/NetworkManager/system-connections/$vpn_name
[connection]
id=$vpn_name
# Create a UUID for this connection
uuid=$(uuidgen)
type=vpn
autoconnect=false
# Get current user and give them permission to this VPN
permissions=user:$(who -m | awk '{print $1;}'):;

[vpn]
gateway=$firewall_ip
ipsec-enabled=yes
ipsec-esp=3des-sha1
ipsec-forceencaps=yes
ipsec-ike=3des-sha1-modp1024
ipsec-psk=$psk
password-flags=0
user=$username
service-type=org.freedesktop.NetworkManager.l2tp

[vpn-secrets]
password=$password

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
sudo systemctl disable xl2tpd

# Connect
# NOTE: If you start or enable either of these at any point, the connection will fail
sudo nmcli con up id $vpn_name

# Disconnect
#sudo nmcli con down id $vpn_name
