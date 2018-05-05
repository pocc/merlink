# -*- mode: python -*-

block_cipher = None


a = Analysis(['src\\merlink.py'],
             pathex=['C:\\Users\\ross.jacobs\\code\\merlink'],
             binaries=[],
             datas=[('src\\media\\', 'media'), ('src\\scripts', 'scripts'), ('LICENSE.txt', '.')],
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
          console=False , icon='src\\media\\miles.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='merlink')
