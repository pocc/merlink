#!/usr/bin/env bash
# Copyright 2018 Ross Jacobs All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Get params
NAME="$1"
VERSION="$2"
echo "Received variables ${NAME} and ${VERSION}."

### Setup for FPM
# Remove problematic file for 18.04 Ubuntu
rm -vf dist/merlink/libdrm.so.2
# Build required directories
mkdir -pv build/usr/bin
mkdir -pv build/opt
# Create a symbolic link to the merlink binary in opt
ln -fsv /opt/merlink/merlink build/usr/bin
# Pyinstaller generates a folder bundle in dist. Move this to opt.
cp -fr dist/merlink build/opt

# package everything in build
cd build

# deb + rpm + tar
OPTIONS="--force --verbose \
    --input-type dir \
    --version ${VERSION} \
    --name ${NAME} \
    --maintainer projectmerlink@gmail.com \
    --license ../LICENSE.txt \
    --architecture amd64 \
    --category Network \
    --url pocc.merlink.io/merlink \
    --vendor MerLink \
    --after-install ../pkg/linux_chmod_ax_script.sh"

echo "Working directory before using fpm: $(pwd)"


# strongswan-plugin-ssl required for Linux Mint 18.3 (other Xenial distros
# come with it by default) Ubuntu 18.04 doesn't have strongswan-plugin-ssl
# though, so not requiring
#   network-manager-l2tp may be helpful in troubleshooting but is not required
# Annoyingly, debian calls it "network-manager" while redhat calls it
# "NetworkManager", so we need separate dependency lists
# folders (usr, opt) MUST be the last arguments
# There are no config files, thus --deb-no-default-config-files
fpm --output-type deb "${OPTIONS}" -p ${NAME}-${VERSION}_x64.deb \
    --description 'Cross-platform VPN editor' \
    --deb-no-default-config-files \
    --deb-priority optional \
    --depends network-manager \
    --depends network-manager-l2tp \
    --deb-suggests network-manager-l2tp-gnome \
    --deb-suggests strongswan-plugin-openssl\
    opt usr
# redhat doesn't believe in suggests. There's a suggestion I'd like to make.
fpm --output-type rpm "${OPTIONS}" -p ${NAME}-${VERSION}_x64.rpm \
    --description 'Cross-platform VPN editor' \
    --depends NetworkManager \
    --depends NetworkManager-l2tp\
    opt usr