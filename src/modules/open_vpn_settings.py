from os import system


def open_windows_vpn_settings():
    # Opens Windows 10 Settings > Network & Internet > VPN
    system('start ms-settings:network-vpn')


def open_macos_vpn_settings():
    # Opens macOS System Settings > Network
    system('open /System/Library/PreferencePanes/Network.prefPane/')


def open_nm_vpn_settings():
    # Opens System Settings > Network
    system('nm-connections-editor')
