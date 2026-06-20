; Sentinel Inno Setup Installer Script
; Compile this in Inno Setup to produce SentinelSetup.exe

[Setup]
AppName=Sentinel
AppVersion=1.2.1
AppPublisher=The Geeks
AppPublisherURL=https://github.com/aditya-gitzy/Sentinel-Linux
AppSupportURL=https://github.com/aditya-gitzy/Sentinel-Linux/issues
DefaultDirName={autopf}\Sentinel
DefaultGroupName=Sentinel
UninstallDisplayName=Sentinel - Real-Time File Router
OutputDir=installer_output
OutputBaseFilename=SentinelSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
AllowNoIcons=yes
SetupIconFile=Sentinel.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"
Name: "startmenu"; Description: "Create a &Start Menu shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
; Include the entire SentinelUI onedir folder
Source: "dist\SentinelUI\Sentinel.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SentinelDaemon.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SentinelUI\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\Sentinel"; Filename: "{app}\Sentinel.exe"; Comment: "Sentinel - Real-Time File Router"
Name: "{group}\Uninstall Sentinel"; Filename: "{uninstallexe}"
; Desktop shortcut (optional, user chooses during install)
Name: "{userdesktop}\Sentinel"; Filename: "{app}\Sentinel.exe"; Tasks: desktopicon; Comment: "Sentinel - Real-Time File Router"

[Run]
; Option to launch Sentinel after installation completes
Filename: "{app}\Sentinel.exe"; Description: "Launch Sentinel now"; Flags: nowait postinstall skipifsilent
