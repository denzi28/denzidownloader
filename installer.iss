#define MyAppName "DenziDownloader"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

[Setup]
AppId={{6F1D2B7A-3C54-4E0B-9A1D-5E0D2A0C0001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest
OutputDir=installer_out
OutputBaseFilename=DenziDownloader-Setup
Compression=lzma2
SolidCompression=yes
UninstallDisplayIcon={app}\DenziDownloader.exe
DisableProgramGroupPage=yes

[Tasks]
Name: "startup"; Description: "Start DenziDownloader in the background when Windows starts (recommended for the browser extension)"; Flags: checkedonce
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: checkedonce

[Files]
Source: "dist\DenziDownloader.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\DenziDownloader.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\DenziDownloader.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "DenziDownloader"; ValueData: """{app}\DenziDownloader.exe"" --background"; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\DenziDownloader.exe"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
