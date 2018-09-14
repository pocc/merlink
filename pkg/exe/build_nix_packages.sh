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
pyinstaller -y pyinstaller.spec

### If Linux make deb, rpm, tar; Elif Macos make dmg; Else Error
if [ $(uname) = 'Linux' ]; then 
	bash pkg/fpm_build.sh ${NAME} ${VERSION}

elif [ $(uname) = 'Darwin' ]; then
	dmgbuild -s pkg/dmg_settings.py "${NAME}" "build/${NAME}-${VERSION}_x64.dmg"

else
	echo "ERROR: Unsupported OS $(uname)"

fi

# Extra debug info for travis
echo "Built targets:"
ls -1d build/* | grep merlink
echo "Deploy targets:"
echo "build/merlink-${VERSION}_x64.deb"
echo "build/merlink-${VERSION}_x64.rpm"
echo "build/merlink-${VERSION}_x64.tar.gz"
echo "build/merlink-${VERSION}_x64.dmg"
