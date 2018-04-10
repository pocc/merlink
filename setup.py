import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=['PyQt5', 'mechanicalsoup', 'requests', 'bs4'], excludes=[])

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('client_vpn.py', base=base)
]

setup(name='Meraki VPN Client',
      version='0.1.0',
      description='PyQt5 VPN Client to connect to Meraki firewalls',
      options=dict(build_exe=buildOptions),
      executables=executables)
