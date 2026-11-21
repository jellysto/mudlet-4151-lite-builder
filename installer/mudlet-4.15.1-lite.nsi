; Mudlet 4.15.1 Lite - NSIS installer script
; Built by .github/workflows/build-mudlet-4151.yml
;
; makensis is invoked with:
;   /DMUDLET_VERSION=4.15.1
;   /DRELEASE_DIR=<...>\Mudlet\src\release

Unicode true

!ifndef MUDLET_VERSION
  !define MUDLET_VERSION "4.15.1"
!endif
!ifndef RELEASE_DIR
  !error "RELEASE_DIR must be defined via /DRELEASE_DIR=..."
!endif

; --- Installer metadata ----------------------------------------------------
Name "Mudlet ${MUDLET_VERSION} Lite"
OutFile "Mudlet-${MUDLET_VERSION}-Lite-Setup.exe"
InstallDir "$PROGRAMFILES64\Mudlet Lite"
InstallDirRegKey HKLM "Software\Mudlet Lite" "Install_Dir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

; --- Modern UI -------------------------------------------------------------
!include "MUI2.nsh"

!define MUI_ABORTWARNING
; Icon is optional: the workflow passes /DMUI_ICON_OVERRIDE=<path> when found.
!ifdef MUI_ICON_OVERRIDE
  !define MUI_ICON "${MUI_ICON_OVERRIDE}"
  !define MUI_UNICON "${MUI_ICON_OVERRIDE}"
!endif
!define MUI_WELCOMEPAGE_TITLE "Mudlet ${MUDLET_VERSION} Lite Setup"
!define MUI_WELCOMEPAGE_TEXT "This will install Mudlet ${MUDLET_VERSION} Lite (updater, 3D mapper, IRC, Discord, speech and spell-check removed).$\r$\n$\r$\nA custom, feature-reduced build. $\r$\nClick Next to continue."

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${RELEASE_DIR}\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

; --- Install section -------------------------------------------------------
Section "Mudlet Lite (required)" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"

  ; Main binary + all runtime files (windeployqt already emitted Qt DLLs/plugins).
  File /r "${RELEASE_DIR}\*.*"

  ; Write install registry + uninstaller.
  WriteRegStr HKLM "Software\Mudlet Lite" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Mudlet Lite" "DisplayName" "Mudlet ${MUDLET_VERSION} Lite"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Mudlet Lite" "DisplayVersion" "${MUDLET_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Mudlet Lite" "Publisher" "Custom build"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Mudlet Lite" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Mudlet Lite" "InstallLocation" "$INSTDIR"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Mudlet Lite" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Mudlet Lite" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; --- Start menu shortcuts --------------------------------------------------
Section "Start Menu Shortcuts" SecShortcuts
  CreateDirectory "$SMPROGRAMS\Mudlet Lite"
  CreateShortcut "$SMPROGRAMS\Mudlet Lite\Mudlet Lite.lnk" "$INSTDIR\Mudlet.exe" "" "$INSTDIR\Mudlet.exe" 0
  CreateShortcut "$SMPROGRAMS\Mudlet Lite\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
SectionEnd

; --- Desktop shortcut (optional) -------------------------------------------
Section "Desktop Shortcut" SecDesktop
  CreateShortcut "$DESKTOP\Mudlet Lite.lnk" "$INSTDIR\Mudlet.exe" "" "$INSTDIR\Mudlet.exe" 0
SectionEnd

; --- Descriptions ----------------------------------------------------------
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain}      "Mudlet client and all required runtime files."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} "Create Start Menu shortcuts."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop}   "Create a desktop shortcut."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; --- Uninstaller -----------------------------------------------------------
Section "Uninstall"
  Delete "$INSTDIR\uninstall.exe"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\Mudlet Lite\Mudlet Lite.lnk"
  Delete "$SMPROGRAMS\Mudlet Lite\Uninstall.lnk"
  RMDir "$SMPROGRAMS\Mudlet Lite"
  Delete "$DESKTOP\Mudlet Lite.lnk"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Mudlet Lite"
  DeleteRegKey HKLM "Software\Mudlet Lite"
SectionEnd
