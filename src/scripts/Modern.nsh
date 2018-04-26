; Script to build an installer/uninstaller that has an icon + startup menu item
;   Place this file in C:\Program Files (x86)\NSIS\contrib\zip2exe to create an
; installer with this configuration and a ZIP bundle of your program files.
;   Make sure to put your data files (icon file and license) in %APPDATA%\Local\Temp
; because that is where the NSIS Zip2Exe is expecting them
;
; Using NSIS v3.03, Modern UI v2
; Written By Ross Jacobs
; TODO
; * [ ] Installer has installer icon
; * [ ] Uninstaller has installer icon with a red circle + diagonal strike through it
; * [ ] Welcome to the Installer (Back grayed out, Next, Cancel)
; * [ ] IF PROGRAM REG KEY: Change, repair, or remove installation (sections for change, repair, remove | back, next, cancel at bottom)
; * [ ] Uninstall option
;   * [ ] Uninstalling deletes the registry key
; * [ ] Show license and terms
;   * [ ] Contact Information - merlinkproject AT-sign gmail.com
;   * [x] Show Apache license
; * [x] Dialog asking where to store them
;   * [ ] OPTION: Start at boot (set selected)
;   * [ ] OPTION: Have startup item (set selected)
;   * [ ] OPTION: Desktop icon (set selected)
; * [x] Install files to directory
;   * [ ] Installing will create a registry key for this program
; * [x] Finish Page "You have successfully installed Merlink!", with links to the github project and stack overflow
;
;

;--------------------------------
; Base settings
  !include "MUI2.nsh"
  !define MUI_ICON miles.ico
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Definitions
  !define APPNAME "MerLink"
  !define DESCRIPTION "A VPN client for Meraki firewalls"

;--------------------------------
;Interface Configuration
  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Header\nsis.bmp" ; optional
  !define MUI_ABORTWARNING

;--------------------------------
; Main Pages
; Shows license
  !insertmacro MUI_PAGE_LICENSE LICENSE.txt
; Asks user which folder to install in
  !insertmacro MUI_PAGE_DIRECTORY
; Puts files into install folder
  !insertmacro MUI_PAGE_INSTFILES

;--------------------------------
; Finish Page
  !define MUI_FINISHPAGE_TITLE "You have successfully installed MerLink!"
  !define MUI_FINISHPAGE_BUTTON "Finish"
; On finish page, show README (redirect to github pages)
  !define MUI_FINISHPAGE_SHOWREADME "https://pocc.github.io/merlink/"
  !define MUI_FINISHPAGE_SHOWREADME_TEXT "Launch a browser to view the README"
  !define MUI_FINISHPAGE_LINK "And here's a link to stack overflow just because."
  !define MUI_FINISHPAGE_LINK_LOCATION "https://stackoverflow.com"
; Actual Macro
  !insertmacro MUI_PAGE_FINISH

;--------------------------------
;Installer Sections
Section "Dummy Section" SecDummy
  SetOutPath "$INSTDIR"
  ;ADD YOUR OWN FILES HERE...
  ;Store installation folder
  WriteRegStr HKCU "Software\Modern UI Test" "" $INSTDIR
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

;--------------------------------
;Descriptions
  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "A test section."
  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section
Section "Uninstall"
  ;ADD YOUR OWN FILES HERE...
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  DeleteRegKey /ifempty HKCU "Software\Modern UI Test"
SectionEnd