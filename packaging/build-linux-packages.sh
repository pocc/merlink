#!/usr/bin/env bash
# This script will build merlink targets using pyinstaller and fpm
# When in doubt, use a force/yes flag to overwrite
# Assume starting directory is ./packaging

# Get variables from setup.py
NAME=$(cat ../setup.py | grep name | cut -d "'" -f2)
VERSION=$(cat ../setup.py | grep version | cut -d "'" -f2)
MINOR_VERSION=$(echo ${VERSION} | cut -d "." -f1,2)
PATCH_VERSION=$(echo ${VERSION} | cut -d "." -f3)

### Create bundle with pyinstaller
# cd to directory root
cd ..
# clean directories first
rm -rf build dist
pyinstaller -y pyinstaller.linux.spec

### Setup for FPM
mkdir -p build/usr/bin
mkdir -p build/opt
# Remove problematic file for 18.04 Ubuntu
rm dist/merlink/libdrm.so.2
# Create a symbolic link to the merlink binary in opt
ln -fs /opt/merlink/merlink build/usr/bin
# Pyinstaller generates a folder bundle in dist. Move this to opt.
mv -f dist/merlink build/opt

### FPM configuration
cd build
# deb + rpm + tar
OPTIONS="--force \
    --input-type dir \
    --version ${MINOR_VERSION} \
    --name ${NAME} \
    --maintainer projectmerlink@gmail.com \
    --license 'opt/merlink/LICENSE.txt' \
    --architecture amd64 \
    --category Network \
    --url pocc.merlink.io/merlink \
    --vendor MerLink"

# strongswan-plugin-ssl required for Linux Mint 18.3 (other Xenial distros come with it by default)
# Ubuntu 18.04 doesn't have strongswan-plugin-ssl though, so not requiring
#   network-manager-l2tp may be helpful in troubleshooting but is not required
# Annoyingly, debian calls it "network-manager" while redhat calls it "NetworkManager",
#   so we need separate dependency lists
# folders (usr, opt) MUST be the last arguments
# There are no config files, thus --deb-no-default-config-files
fpm --output-type deb ${OPTIONS} -p ${NAME}-${MINOR_VERSION}.deb --description 'Cross-platform VPN editor' \
    --deb-no-default-config-files \
    --depends network-manager \
    --depends network-manager-l2tp \
    --deb-suggests network-manager-l2tp-gnome \
    --deb-suggests strongswan-plugin-openssl\
    usr opt
# redhat doesn't believe in suggests. There's a suggestion I'd like to make.
fpm --output-type rpm ${OPTIONS} -p ${NAME}-${MINOR_VERSION}.rpm --description 'Cross-platform VPN editor' \
    --depends NetworkManager \
    --depends NetworkManager-l2tp\
    usr opt
# Do not require anything so tar can just work everywhere
fpm --output-type tar ${OPTIONS} -p ${NAME}-${MINOR_VERSION}.tar --description 'Cross-platform VPN editor' usr opt

# pacman (is failing on my system, but need confirmation)
# ERRORS:
#     Process failed: /bin/bash failed (exit code 127). Full command was:["/bin/bash", "-c", "LANG=C bsdtar -czf .MTREE --format=mtree --options='!all,use-set,type,uid,gid,mode,time,size,md5,sha256,link' var .PKGINFO"] {:level=>:error}
#fpm -f -s dir -t pacman -v ${VERSION} -n ${NAME} -p build/${NAME}-${VERSION}.pacman build/usr build/opt
# .tar.gz.     Using fpm and not tar for consistency.
