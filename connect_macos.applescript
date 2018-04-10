# Worth mentioning: https://github.com/halo/macosvpn
# TODO test this and see if it works on a MAC
# Stolen from https://stackoverflow.com/questions/32957121/in-mac-os-x-10-11-opening-a-vpn-connection-window-with-the-command-line-gives-m
set vpn_name to "'Meraki VPN (L2TP'"
set user_name to "my_user_name"
set otp_token to "XYZXYZABCABC"

tell application "System Events"
    set rc to do shell script "scutil --nc status " & vpn_name
    if rc starts with "Connected" then
        do shell script "scutil --nc stop " & vpn_name
    else
        set PWScript to "security find-generic-password -D \"802.1X Password\" -w -a " & user_name
        set passwd to do shell script PWScript
        -- installed through "brew install oath-toolkit"
        set OTPScript to "/usr/local/bin/oathtool --totp --base32 " & otp_token
        set otp to do shell script OTPScript
        do shell script "scutil --nc start " & vpn_name & " --user " & user_name
        delay 2
        keystroke passwd
        keystroke otp
        keystroke return
    end if
end tell