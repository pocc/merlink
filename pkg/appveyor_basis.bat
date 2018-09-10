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

# Will package merlink into an exe from source files.
# This file is the basis for the .appveyor script.

$env:Path = "C:\Program Files (x86)\NSIS"
cd %TEMP%
git clone https://github.com/pocc/merlink
cd merlink
python3 easy_install
python3 -m pip install -r requirements.txt
GIT_VERSION=git describe --abrev=0 --tags

pyinstaller merlink.spec
# /D specifies additional variables to be used in the script
makensis /DPRODUCT_VERSION=GIT_VERSION .\pkg\windows_nsis_installer.nsh