#!/usr/bin/env bash
# This file will contain bash/strongswan commands to modify VPN settings
# This looks promising: http://www.jasonernst.com/2016/06/21/l2tp-ipsec-vpn-on-ubuntu-16-04/
# Test it out in a virtual machine

# Assign values from positional parameters
echo "Inside of connect_linux.sh"
primary_ip=$1
username=$2
password=$3

echo "Your IP, username, and password are: " $primary_ip $username $password
echo "Exiting connect_linux.sh"

# Return 0 if successful, 1 on failure
vpn_connection="successful"
if [ $vpn_connection = "successful" ]; then
    (exit 0)
else
    (exit 1)
fi