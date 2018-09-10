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

"""This spec file is used by pyinstaller as a settings file

Analysis:
    [File.py]: The program's entry point
    binaries: Any compiled libraries (.so, .pyd, etc.)
    datas: Where to look for additional files
    hiddenimports: What libraries not in the entrypoint that should be included
    excludes: Libraries to exclude. PyInstaller's default behavior is to play it
        safe by including EVERYTHING. Using here to remove unneeded libraries.

exe: Should be run on Windows only
app: Should be run on macOS only
coll: Should be run on all OSes


Required modules (i.e. can't add to excludes):
    '__future__',  # urllib3
    'calendar',
    'cgi',
    'codecs',
    'datetime',
    'email',  # urllib3
    'tarfile',  # webbrowser
    'urllib3.poolmanager',
    'xml',
"""

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
             excludes=[
                'PyQt5.QtBluetooth',
                'PyQt5.QtDBus',
                'PyQt5.QtDesigner',
                'PyQt5.QtHelp',
                'PyQt5.QtLocation',
                'PyQt5.QtMultimedia',
                'PyQt5.QtMultimediaWidgets',
                'PyQt5.QtNetwork',
                'PyQt5.QtNetworkAuth',
                'PyQt5.QtNfc',
                'PyQt5.QtOpenGL',
                'PyQt5.QtPositioning',
                'PyQt5.QtPrintSupport',
                'PyQt5.QtQml',
                'PyQt5.QtQuick',
                'PyQt5.QtQuickWidgets',
                'PyQt5.QtSensors',
                'PyQt5.QtSerialPort',
                'PyQt5.QtSql',
                'PyQt5.QtSvg',
                'PyQt5.QtTest',
                'PyQt5.QtWebChannel',
                'PyQt5.QtWebEngine',
                'PyQt5.QtWebEngineCore',
                'PyQt5.QtWebEngineWidgets',
                'PyQt5.QtWebSockets',
                'PyQt5.QtX11Extras',
                'PyQt5.QtXml',
                'PyQt5.QtXmlPatterns',

                # Testing shows these libraries can be excluded (1MB saved).
                # Remove from excludes if their absence causes issues.
                'bz2',
                'difflib',
                'ftplib',
                'lib2to3',
                'multiprocessing',
                'pkg_resources',
            ],
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
