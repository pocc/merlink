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
; TODO
; * [x] Installer has installer icon
; * [x] Uninstaller has installer icon with a red circle + diagonal strike through it
; * [x] Welcome to the Installer
; * [ ] IF PROGRAM REG KEY: Change, repair, or remove installation (sections for change, repair, remove | back, next, cancel at bottom)
; * [ ] Uninstall option
;   * [ ] Uninstalling deletes the registry key
; * [x] Show license and terms
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


; ${PROGRAM_NAME} is defined as part of setup process
; TODO 64bit vs 32bit

; Base settings
    !include "MUI2.nsh"
    !define MUI_ICON miles.ico
    !define MUI_UNICON unmiles.ico
    !define VERSION '0.2.1'
    BrandingText "Merlink v${VERSION}"

;--------------------------------
; Definitions
    !define NAME 'Merlink'
    !define PRODUCT_WEBSITE 'https://pocc.github.io/merlink/'
    !define DESCRIPTION 'A VPN client for Meraki firewalls'

    ; Set output file for executable and destination for installation files
    outfile '${NAME}.exe'
	InstallDir '$PROGRAMFILES\${NAME}'

    SetOverwrite ifnewer
    CRCCheck on

;--------------------------------
;Interface Configuration
   ; !define MUI_HEADERIMAGE
    ;!define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Header\nsis.bmp" ; optional
    ;!define MUI_ABORTWARNING

;--------------------------------
; INSTALLER PAGES
; Welcome Page
	!define WELCOME_TITLE 'Welcome to Merlink ${VERSION} setup!'
	!define MUI_WELCOMEPAGE_TITLE '${WELCOME_TITLE}'
    !insertmacro MUI_PAGE_WELCOME

    ; You can override the welcome page text and left-side bitmap; however, the default is best for most use cases
    ;!define MUI_WELCOMEFINISHPAGE_BITMAP nsis3.bmp
    ;!define MUI_WELCOMEPAGE_TEXT ""

; Shows license
    !insertmacro MUI_PAGE_LICENSE LICENSE.txt

; Asks user which folder to install in
    !insertmacro MUI_PAGE_DIRECTORY
; Puts files into install folder
    !insertmacro MUI_PAGE_INSTFILES

    !insertmacro MUI_UNPAGE_WELCOME
	!insertmacro MUI_UNPAGE_CONFIRM
	!insertmacro MUI_UNPAGE_DIRECTORY
	!insertmacro MUI_UNPAGE_INSTFILES
	!insertmacro MUI_UNPAGE_FINISH



;--------------------------------
; INSTALLATION REGEDITS
Section "Install"
	; Start on startup
	; Uninstall Keys
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Merlink" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""  ; Uninstall by UninstallString
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Merlink" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\""  ; Uninstall by UninstallString, /S makes it silent installer
SectionEnd

;--------------------------------
; UNINSTALLER PAGES
; Uninstall page, confirmation, showing directory to remove, removing files, and finish should be sufficient

Section "Uninstall"
;Delete Files
  RMDir /r "$INSTDIR\*.*"

;Remove the installation directory
  RMDir "$INSTDIR"

;Delete Start Menu Shortcuts
  Delete "$DESKTOP\${NAME}.lnk"
  Delete "$SMPROGRAMS\${NAME}\*.*"
  RmDir  "$SMPROGRAMS\${NAME}"

;Delete Uninstaller And Unistall Registry Entries
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\${NAME}"
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}"
SectionEnd

;--------------------------------
; Finish Page
    !define MUI_FINISHPAGE_TITLE "You have successfully installed MerLink!"
    !define MUI_FINISHPAGE_BUTTON "Finish"
    !define MUI_FINISHPAGE_RUN "$INSTDIR\Merlink.exe"
	!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
	!define MUI_FINISHPAGE_SHOWREADME_FUNCTION CreateDesktopShortcut
    !define MUI_FINISHPAGE_LINK "View the source on GitHub!"
    !define MUI_FINISHPAGE_LINK_LOCATION "${PRODUCT_WEBSITE}"
    ; We shouldn't have to reboot after installation of this application, so don't show users that option
    !define MUI_FINISHPAGE_NOREBOOTSUPPORT
; Actual Macro
    !insertmacro MUI_PAGE_FINISH

function CreateDesktopShortcut
	; Create startup directory and Desktop icon
	setShellVarContext all
	createDirectory "$SMPROGRAMS\${NAME}"
	createShortCut "$SMPROGRAMS\${NAME}.lnk" "$INSTDIR\${NAME}.exe" "$INSTDIR\src\media\miles.ico"
	createShortcut "$DESKTOP\${NAME}.lnk" "$INSTDIR\${NAME}.exe" ""
functionEnd

; ============================================================================
; MUI Languages
; ============================================================================
; Language: PUT AT BOTTOM OR INSTALLER BREAKS!!!
    !insertmacro MUI_LANGUAGE "English"


;---------------------------------------------------------------------------------------------------------------------