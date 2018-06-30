#!/usr/bin/env bash
# This script will build merlink targets using pyinstaller and fpm
# When in doubt, use a force/yes flag to overwrite

### Set up environment
mkdir -pv build
echo "Entering working directory: $(pwd)"
# Get version from git tag
GIT_VERSION=$(git describe --abbrev=0 --tags)
# Remove preceding 'v' from version
VERSION=${GIT_VERSION:1}
NAME='merlink'

### Create bundle with pyinstaller
pyinstaller -y pyinstaller.nix.spec

### If Linux make deb, rpm, tar; Elif Macos make dmg; Else Error
if [ $(uname) = 'Linux' ]; then 
	bash pkg/fpm_build.sh ${NAME} ${VERSION}

elif [ $(uname) = 'Darwin' ]; then
	dmgbuild -s pkg/dmg_settings.py "${NAME}" build/${NAME}-${VERSION}.dmg

else
	echo "ERROR: Unsupported OS $(uname)"

fi
