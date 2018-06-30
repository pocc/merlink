# -*- mode: python -*-
# This spec file is used by pyinstaller on linux as a settings file

block_cipher = None

# Adding runtime hooks per https://github.com/pyinstaller/pyinstaller/issues/1713
a = Analysis(['merlink.py'],
             binaries=[],
             datas=[('src', 'src'), ('LICENSE.txt', '.')],
             hiddenimports=[],
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
