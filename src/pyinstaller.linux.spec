# -*- mode: python -*-
# This spec file is used by pyinstaller on linux as a settings file

block_cipher = None


a = Analysis(['merlink.py'],
             pathex=['~/code/merlink'],
             binaries=[],
             datas=[('media/', 'media'), ('scripts', 'scripts'), ('../LICENSE.txt', '.')],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='merlink',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='src/media/miles.ico')
