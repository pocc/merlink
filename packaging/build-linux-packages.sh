#!/usr/bin/env bash
# This script will build merlink targets using pyinstaller and fpm
# When in doubt, use a force/yes flag to overwrite

# Get variables from setup.py
NAME=$(cat ../setup.py | grep name | cut -d "'" -f2)
VERSION=$(cat ../setup.py | grep version | cut -d "'" -f2)


### Create bundle with pyinstaller
# cd to directory root
cd ..
# clean directories first
rm -rf build dist
pyinstaller -y pyinstaller.linux.spec

### Setup for FPM
mkdir -p build/usr/bin
mkdir -p build/opt
# Create a symbolic link to the merlink binary in opt
ln -fs /opt/merlink/merlink build/usr/bin
# Pyinstaller generates a folder bundle in dist. Move this to opt.
mv -f dist/merlink build/opt

### FPM configuration
cd build
# deb + rpm + tar
fpm -f -s dir -t deb -v ${VERSION} -n ${NAME} -p ${NAME}-${VERSION}.deb usr opt
fpm -f -s dir -t rpm -v ${VERSION} -n ${NAME} -p ${NAME}-${VERSION}.rpm usr opt
fpm -f -s dir -t tar -v ${VERSION} -n ${NAME} -p ${NAME}-${VERSION}.tar.gz usr opt
# pacman (is failing on my system, but need confirmation)
# ERRORS:
#     Process failed: /bin/bash failed (exit code 127). Full command was:["/bin/bash", "-c", "LANG=C bsdtar -czf .MTREE --format=mtree --options='!all,use-set,type,uid,gid,mode,time,size,md5,sha256,link' var .PKGINFO"] {:level=>:error}
#fpm -f -s dir -t pacman -v ${VERSION} -n ${NAME} -p build/${NAME}-${VERSION}.pacman build/usr build/opt
# .tar.gz.     Using fpm and not tar for consistency.
