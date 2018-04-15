import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=["os", "idna", "queue"], excludes=["tkinter"])
includes = ['login_window']
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('./src/vpn_client.py', base=base)
]

setup(name='Merlink',
      version='0.1.0',
      description='PyQt based VPN client for Meraki firewalls',
      options=dict(build_exe=buildOptions),
      executables=executables)
