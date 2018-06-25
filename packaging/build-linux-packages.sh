#!/usr/bin/env bash
# This script will build merlink targets using pyinstaller and fpm
# When in doubt, use a force/yes flag to overwrite

echo "Entering working directory: $(pwd)"
# If we're not running in Travis CI, throw an error
if [ -z $TRAVIS_TAG ]; then
    TRAVIS_TAG='Leprechaun.Gold'
fi
NAME='merlink'

### Create bundle with pyinstaller
pyinstaller -y pyinstaller.linux.spec

### Setup for FPM
mkdir -pv bin/usr/bin
mkdir -pv bin/opt
# Remove problematic file for 18.04 Ubuntu
rm -vf dist/merlink/libdrm.so.2
# Create a symbolic link to the merlink binary in opt
ln -fsv /opt/merlink/merlink bin/usr/bin
# Pyinstaller generates a folder bundle in dist. Move this to opt.
cp -fvr dist/merlink bin/opt

### FPM configuration
cd bin
# deb + rpm + tar
OPTIONS="--force --verbose \
    --input-type dir \
    --version ${TRAVIS_TAG} \
    --name ${NAME} \
    --maintainer projectmerlink@gmail.com \
    --license 'opt/merlink/LICENSE.txt' \
    --architecture amd64 \
    --category Network \
    --url pocc.merlink.io/merlink \
    --vendor MerLink"

echo "Working directory before using fpm: $(pwd)"
# strongswan-plugin-ssl required for Linux Mint 18.3 (other Xenial distros come with it by default)
# Ubuntu 18.04 doesn't have strongswan-plugin-ssl though, so not requiring
#   network-manager-l2tp may be helpful in troubleshooting but is not required
# Annoyingly, debian calls it "network-manager" while redhat calls it "NetworkManager",
#   so we need separate dependency lists
# folders (usr, opt) MUST be the last arguments
# There are no config files, thus --deb-no-default-config-files
fpm --output-type deb ${OPTIONS} -p ${NAME}-${TRAVIS_TAG}.deb --description 'Cross-platform VPN editor' \
    --deb-no-default-config-files \
    --deb-priority optional \
    --depends network-manager \
    --depends network-manager-l2tp \
    --deb-suggests network-manager-l2tp-gnome \
    --deb-suggests strongswan-plugin-openssl\
    opt usr
# redhat doesn't believe in suggests. There's a suggestion I'd like to make.
fpm --output-type rpm ${OPTIONS} -p ${NAME}-${TRAVIS_TAG}.rpm --description 'Cross-platform VPN editor' \
    --depends NetworkManager \
    --depends NetworkManager-l2tp\
    opt usr
# Do not require anything so tar can just work everywhere
tar cvzf ${NAME}-${TRAVIS_TAG}.tar.gz opt usr

# Removing non-packages from bin directory
# rm -rfv opt usr

# pacman (is failing on my system, but need confirmation)
# ERRORS:
#     Process failed: /bin/bash failed (exit code 127). Full command was:["/bin/bash", "-c", "LANG=C bsdtar -czf .MTREE --format=mtree --options='!all,use-set,type,uid,gid,mode,time,size,md5,sha256,link' var .PKGINFO"] {:level=>:error}
#fpm -f -s dir -t pacman -v ${TRAVIS_TAG} -n ${NAME} -p bin/${NAME}-${TRAVIS_TAG}.pacman bin/usr bin/opt
# .tar.gz.     Using fpm and not tar for consistency.
