; NSIS Script to build an installer/uninstaller that has an icon + startup menu item
; Download NSIS: https://sourceforge.net/projects/nsis/ (link works as of 2018-04-25)
;   Place this file in C:\Program Files (x86)\NSIS\contrib\zip2exe to create an
; installer with this configuration and a ZIP bundle of your program files.
;   Make sure to put your data files (icon file and license) in %APPDATA%\Local\Temp
; because that is where the NSIS Zip2Exe is expecting them
;
; Read this documentation if you are trying to create your own NSIS script:
; http://nsis.sourceforge.net/Docs/Modern%20UI%202/Readme.html
;
; Using NSIS v3.03, Modern UI v2
; Written By Ross Jacobs
;

!define SOURCE_FILES "..\dist\merlink"
# PRODUCT_VERSION should be passed in with the /D flag
!define PRODUCT_NAME "Merlink"
!define PRODUCT_PUBLISHER "Merlink"
!define PRODUCT_WEBSITE "https://pocc.github.io/merlink"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\merlink.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_DESCRIPTION 'A VPN client for Meraki firewalls'
BrandingText "Merlink v${PRODUCT_VERSION}"


SetCompressor /SOLID lzma

; MUI 2 compatible ------
!include "MUI2.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${SOURCE_FILES}\src\media\miles.ico"
!define MUI_UNICON "${SOURCE_FILES}\src\media\unmiles.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "${SOURCE_FILES}\LICENSE.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish Page
!define MUI_FINISHPAGE_TITLE "You have successfully installed MerLink!"
!define MUI_FINISHPAGE_BUTTON "Finish"
!define MUI_FINISHPAGE_RUN "$INSTDIR\merlink.exe"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION CreateDesktopShortcut
!define MUI_FINISHPAGE_LINK "View the source on GitHub!"
!define MUI_FINISHPAGE_LINK_LOCATION "${PRODUCT_WEBSITE}"
; We shouldn't have to reboot after installation of this application, so don't show users that option
!define MUI_FINISHPAGE_NOREBOOTSUPPORT
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH


; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Merlink-${PRODUCT_VERSION}_x64.exe"
InstallDir "$PROGRAMFILES\Merlink"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite try
  File /r "${SOURCE_FILES}\*"

  ; Shortcuts
  ;CreateDirectory "$SMPROGRAMS\Merlink" ; To use a directory (also see uninstall list)
  CreateShortCut "$SMPROGRAMS\Merlink.lnk" "$INSTDIR\merlink.exe"
  CreateShortCut "$DESKTOP\Merlink.lnk" "$INSTDIR\merlink.exe"
  CreateShortCut "$STARTMENU.lnk" "$INSTDIR\merlink.exe"
  CreateShortCut "$QUICKLAUNCH.lnk" "$INSTDIR\merlink.exe"
  CreateShortCut "$SMSTARTUP\Merlink.lnk" "$INSTDIR\Merlink.exe" ; Start on login by putting link in startup folder
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\merlink.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\merlink.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEBSITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components? THIS WILL REMOVE THE MERLINK INSTALL DIRECTORY!" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  RMDir /r /REBOOTOK "$INSTDIR"

  ; Shortcuts
  ;RMDir "$SMPROGRAMS\Merlink" ; To use a directory (also see install list)
  Delete "$SMPROGRAMS\Merlink\Uninstall.lnk"
  Delete "$SMPROGRAMS\Merlink\Website.lnk"
  Delete "$QUICKLAUNCH.lnk"
  Delete "$STARTMENU.lnk"
  Delete "$DESKTOP\Merlink.lnk"
  Delete "$SMPROGRAMS\Merlink.lnk"
  Delete "$SMSTARTUP\Merlink.lnk"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
