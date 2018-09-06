# -*- mode: python -*-
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

# This spec file is used by pyinstaller on linux as a settings file

block_cipher = None

a = Analysis(['merlink.py'],
             binaries=[],
             datas=[('src', 'src'), ('LICENSE.txt', '.')],
             hiddenimports=[
                'psutil',
                'json',
                'requests',
                'mechanicalsoup',
                'PyQt5',
                'PyQt5.QtWidgets',
                'PyQt5.Qt',
                'PyQt5.sip'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='merlink',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='src/media/miles.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='merlink')
app = BUNDLE(coll,
             name='merlink.app',
             icon='./src/media/miles.icns',
             bundle_identifier=None)
