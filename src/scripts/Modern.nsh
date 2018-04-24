; Script to build an installer/uninstaller that has an icon + startup menu item
;   Place this file in C:\Program Files (x86)\NSIS\contrib\zip2exe to create an
; installer with this configuration and a ZIP bundle of your program files.
;   Make sure to put your data files (icon file and license) in %APPDATA%\Local\Temp
; because that is where the NSIS Zip2Exe is expecting them
; -----------------------------------------------------------------------------
; Using NSIS v3.03, Modern UI v2
; Written By Ross Jacobs

; Base settings
  !include "MUI2.nsh"
  !define MUI_ICON miles.ico
  !insertmacro MUI_LANGUAGE "English"

; Definitions
  !define APPNAME "MerLink"
  !define DESCRIPTION "A VPN client for Meraki firewalls"

; Main Pages
; Shows license
  !insertmacro MUI_PAGE_LICENSE LICENSE.txt
; Asks user which folder to install in
  !insertmacro MUI_PAGE_DIRECTORY
; Puts files into install folder
  !insertmacro MUI_PAGE_INSTFILES

; You installed the program! Here's more info
  !define MUI_FINISHPAGE_TITLE "You have successfully installed MerLink!"
  !define MUI_FINISHPAGE_BUTTON "Finish"
; On finish page, show README (redirect to github pages)
  !define MUI_FINISHPAGE_SHOWREADME "https://pocc.github.io/merlink/"
  !define MUI_FINISHPAGE_SHOWREADME_TEXT "Launch a browser to view the README"
  !define MUI_FINISHPAGE_LINK "And here's a link to stack overflow just because."
  !define MUI_FINISHPAGE_LINK_LOCATION "https://stackoverflow.com"
; Actual Macro 
  !insertmacro MUI_PAGE_FINISH
