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

!define PRODUCT_NAME "Merlink"
!define PRODUCT_VERSION "0.3.0"
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
!define MUI_ICON "C:\Users\ross.jacobs\code\merlink\src\media\miles.ico"
!define MUI_UNICON "C:\Users\ross.jacobs\code\merlink\src\media\unmiles.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "C:\Users\ross.jacobs\code\merlink\LICENSE.txt"
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

;;;;; Uninstaller pages ;;;;;
; Sane things you can add to uninstaller
; !insertmacro MUI_UNPAGE_WELCOME
; !insertmacro MUI_UNPAGE_CONFIRM
; !insertmacro MUI_UNPAGE_FINISH
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Merlink-${PRODUCT_VERSION}-setup.exe"
InstallDir "$PROGRAMFILES\Merlink"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show
!define PROGRAM_BUNDLE_DIR "C:\PATH\TO\WHERE\YOU\CREATED\THE\PROGRAM\FILES\WITH\PYINSTALLER"

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite try
  File "${PROGRAM_BUNDLE_DIR}\base_library.zip"
  SetOutPath "$INSTDIR\certifi"
  File "${PROGRAM_BUNDLE_DIR}\certifi\cacert.pem"
  SetOutPath "$INSTDIR"
  File "${PROGRAM_BUNDLE_DIR}\lxml.etree.pyd"
  File "${PROGRAM_BUNDLE_DIR}\lxml._elementpath.pyd"
  SetOutPath "$INSTDIR\media"
  File "${PROGRAM_BUNDLE_DIR}\media\checkmark-16.png"
  File "${PROGRAM_BUNDLE_DIR}\media\dark_miles.png"
  File "${PROGRAM_BUNDLE_DIR}\media\meraki_connections.png"
  File "${PROGRAM_BUNDLE_DIR}\media\miles.ico"
  File "${PROGRAM_BUNDLE_DIR}\media\new-mr.jpg"
  File "${PROGRAM_BUNDLE_DIR}\media\new_mx.jpg"
  File "${PROGRAM_BUNDLE_DIR}\media\sm.jpg"
  File "${PROGRAM_BUNDLE_DIR}\media\transparent_miles.png"
  File "${PROGRAM_BUNDLE_DIR}\media\unmiles.ico"
  File "${PROGRAM_BUNDLE_DIR}\media\x-mark-16.png"
  SetOutPath "$INSTDIR"
  File "${PROGRAM_BUNDLE_DIR}\merlink.exe"
  CreateDirectory "$SMPROGRAMS\Merlink"
  CreateShortCut "$SMPROGRAMS\Merlink\Merlink.lnk" "$INSTDIR\merlink.exe"
  CreateShortCut "$DESKTOP\Merlink.lnk" "$INSTDIR\merlink.exe"
  CreateShortCut "$STARTMENU.lnk" "$INSTDIR\merlink.exe"
  CreateShortCut "$SMPROGRAMS.lnk" "$INSTDIR\merlink.exe"
  CreateShortCut "$QUICKLAUNCH.lnk" "$INSTDIR\merlink.exe"
  File "${PROGRAM_BUNDLE_DIR}\merlink.exe.manifest"
  File "${PROGRAM_BUNDLE_DIR}\MSVCP140.dll"
  File "${PROGRAM_BUNDLE_DIR}\pyexpat.pyd"
  SetOutPath "$INSTDIR\PyQt5\Qt\bin"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\bin\qt.conf"
  SetOutPath "$INSTDIR\PyQt5\Qt\plugins\iconengines"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\iconengines\qsvgicon.dll"
  SetOutPath "$INSTDIR\PyQt5\Qt\plugins\imageformats"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\imageformats\qgif.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\imageformats\qicns.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\imageformats\qico.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\imageformats\qjpeg.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\imageformats\qsvg.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\imageformats\qtga.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\imageformats\qtiff.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\imageformats\qwbmp.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\imageformats\qwebp.dll"
  SetOutPath "$INSTDIR\PyQt5\Qt\plugins\platforms"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\platforms\qminimal.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\platforms\qoffscreen.dll"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\platforms\qwindows.dll"
  SetOutPath "$INSTDIR\PyQt5\Qt\plugins\printsupport"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5\Qt\plugins\printsupport\windowsprintersupport.dll"
  SetOutPath "$INSTDIR"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5.Qt.pyd"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5.QtCore.pyd"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5.QtGui.pyd"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5.QtPrintSupport.pyd"
  File "${PROGRAM_BUNDLE_DIR}\PyQt5.QtWidgets.pyd"
  File "${PROGRAM_BUNDLE_DIR}\python3.dll"
  File "${PROGRAM_BUNDLE_DIR}\python36.dll"
  File "${PROGRAM_BUNDLE_DIR}\pywintypes36.dll"
  File "${PROGRAM_BUNDLE_DIR}\Qt5Core.dll"
  File "${PROGRAM_BUNDLE_DIR}\Qt5Gui.dll"
  File "${PROGRAM_BUNDLE_DIR}\Qt5PrintSupport.dll"
  File "${PROGRAM_BUNDLE_DIR}\Qt5Svg.dll"
  File "${PROGRAM_BUNDLE_DIR}\Qt5Widgets.dll"
  SetOutPath "$INSTDIR\scripts"
  File "${PROGRAM_BUNDLE_DIR}\scripts\connect_linux.sh"
  File "${PROGRAM_BUNDLE_DIR}\scripts\connect_macos.applescript"
  File "${PROGRAM_BUNDLE_DIR}\scripts\connect_windows.ps1"
  File "${PROGRAM_BUNDLE_DIR}\scripts\Modern.nsh"
  SetOutPath "$INSTDIR"
  File "${PROGRAM_BUNDLE_DIR}\select.pyd"
  File "${PROGRAM_BUNDLE_DIR}\sip.pyd"
  File "${PROGRAM_BUNDLE_DIR}\unicodedata.pyd"
  File "${PROGRAM_BUNDLE_DIR}\VCRUNTIME140.dll"
  File "${PROGRAM_BUNDLE_DIR}\win32wnet.pyd"
  File "${PROGRAM_BUNDLE_DIR}\_bz2.pyd"
  File "${PROGRAM_BUNDLE_DIR}\_ctypes.pyd"
  File "${PROGRAM_BUNDLE_DIR}\_hashlib.pyd"
  File "${PROGRAM_BUNDLE_DIR}\_lzma.pyd"
  File "${PROGRAM_BUNDLE_DIR}\_socket.pyd"
  File "${PROGRAM_BUNDLE_DIR}\_ssl.pyd"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEBSITE}"
  CreateShortCut "$SMPROGRAMS\Merlink.lnk" "$INSTDIR\merlink.exe"

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
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\_ssl.pyd"
  Delete "$INSTDIR\_socket.pyd"
  Delete "$INSTDIR\_lzma.pyd"
  Delete "$INSTDIR\_hashlib.pyd"
  Delete "$INSTDIR\_ctypes.pyd"
  Delete "$INSTDIR\_bz2.pyd"
  Delete "$INSTDIR\win32wnet.pyd"
  Delete "$INSTDIR\VCRUNTIME140.dll"
  Delete "$INSTDIR\unicodedata.pyd"
  Delete "$INSTDIR\sip.pyd"
  Delete "$INSTDIR\select.pyd"
  Delete "$INSTDIR\scripts\Modern.nsh"
  Delete "$INSTDIR\scripts\connect_windows.ps1"
  Delete "$INSTDIR\scripts\connect_macos.applescript"
  Delete "$INSTDIR\scripts\connect_linux.sh"
  Delete "$INSTDIR\Qt5Widgets.dll"
  Delete "$INSTDIR\Qt5Svg.dll"
  Delete "$INSTDIR\Qt5PrintSupport.dll"
  Delete "$INSTDIR\Qt5Gui.dll"
  Delete "$INSTDIR\Qt5Core.dll"
  Delete "$INSTDIR\pywintypes36.dll"
  Delete "$INSTDIR\python36.dll"
  Delete "$INSTDIR\python3.dll"
  Delete "$INSTDIR\PyQt5.QtWidgets.pyd"
  Delete "$INSTDIR\PyQt5.QtPrintSupport.pyd"
  Delete "$INSTDIR\PyQt5.QtGui.pyd"
  Delete "$INSTDIR\PyQt5.QtCore.pyd"
  Delete "$INSTDIR\PyQt5.Qt.pyd"
  Delete "$INSTDIR\PyQt5\Qt\plugins\printsupport\windowsprintersupport.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\platforms\qwindows.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\platforms\qoffscreen.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\platforms\qminimal.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\imageformats\qwebp.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\imageformats\qwbmp.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\imageformats\qtiff.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\imageformats\qtga.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\imageformats\qsvg.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\imageformats\qjpeg.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\imageformats\qico.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\imageformats\qicns.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\imageformats\qgif.dll"
  Delete "$INSTDIR\PyQt5\Qt\plugins\iconengines\qsvgicon.dll"
  Delete "$INSTDIR\PyQt5\Qt\bin\qt.conf"
  Delete "$INSTDIR\pyexpat.pyd"
  Delete "$INSTDIR\MSVCP140.dll"
  Delete "$INSTDIR\merlink.exe.manifest"
  Delete "$INSTDIR\merlink.exe"
  Delete "$INSTDIR\media\x-mark-16.png"
  Delete "$INSTDIR\media\unmiles.ico"
  Delete "$INSTDIR\media\transparent_miles.png"
  Delete "$INSTDIR\media\sm.jpg"
  Delete "$INSTDIR\media\new_mx.jpg"
  Delete "$INSTDIR\media\new-mr.jpg"
  Delete "$INSTDIR\media\miles.ico"
  Delete "$INSTDIR\media\meraki_connections.png"
  Delete "$INSTDIR\media\dark_miles.png"
  Delete "$INSTDIR\media\checkmark-16.png"
  Delete "$INSTDIR\lxml._elementpath.pyd"
  Delete "$INSTDIR\lxml.etree.pyd"
  Delete "$INSTDIR\certifi\cacert.pem"
  Delete "$INSTDIR\base_library.zip"

  Delete "$SMPROGRAMS\Merlink\Uninstall.lnk"
  Delete "$SMPROGRAMS\Merlink\Website.lnk"
  Delete "$QUICKLAUNCH.lnk"
  Delete "$SMPROGRAMS.lnk"
  Delete "$STARTMENU.lnk"
  Delete "$DESKTOP\Merlink.lnk"
  Delete "$SMPROGRAMS\Merlink\Merlink.lnk"

  RMDir "$SMPROGRAMS\Merlink"
  RMDir "$INSTDIR\scripts"
  RMDir "$INSTDIR\PyQt5\Qt\plugins\printsupport"
  RMDir "$INSTDIR\PyQt5\Qt\plugins\platforms"
  RMDir "$INSTDIR\PyQt5\Qt\plugins\imageformats"
  RMDir "$INSTDIR\PyQt5\Qt\plugins\iconengines"
  RMDir "$INSTDIR\PyQt5\Qt\bin"
  RMDir "$INSTDIR\media"
  RMDir "$INSTDIR\certifi"
  RMDir "$INSTDIR"
  RMDir ""

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd