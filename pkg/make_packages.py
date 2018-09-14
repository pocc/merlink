#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
"""Create an installable package for this platform."""
import sys
import subprocess
from src.__version__ import __version__

unixlike = True
opensource = True

# Numbers arbitrarily chosen
if sys.platform == 'win32':
    unixlike = False
    opensource = False
elif sys.platform == 'darwin':
    opensource = False

if unixlike:
    # Set up environment
    subprocess.call(['mkdir -pv build'], shell=True)
    subprocess.call(['pwd'], shell=True)
    # Get version from git tag
    # Remove preceding 'v' from version
    if opensource:
        print("Calling linux fpm deb/rpm creator...")
        subprocess.call(['chmod a+x pkg/pkg_linux_fpm.sh'], shell=True)
        subprocess.call(['bash pkg/pkg_linux_fpm.sh merlink ' +
                         __version__], shell=True)
    else:
        print("Calling macos dmgbuild...")
        package_name = "build/merlink-" + __version__ + "_x64.dmg"
        subprocess.call(['dmgbuild', '-s', 'pkg/pkg_macos_dmg.py',
                         'merlink', package_name], shell=True)

    # Extra debug info for travis
    print("Built targets:")
    subprocess.call(['ls -1d build/* | grep merlink'], shell=True)

else:
    print("Calling windows makensis exe creator...")
    subprocess.call(['makensis /DPRODUCT_VERSION=' + __version__ +
                     ' .\pkg\pkg_windows_nsis.nsh'], shell=True)
