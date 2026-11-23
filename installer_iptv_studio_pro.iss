[Setup]
AppName=IPTV Studio Pro
AppVersion=2.0
DefaultDirName={autopf}\IPTV Studio Pro
DefaultGroupName=IPTV Studio Pro
OutputDir=Installer_Output
OutputBaseFilename=IPTV_Studio_Pro_Setup
SetupIconFile=iptv_studio_pro.ico
UninstallDisplayIcon={app}\IPTV_Studio_Pro.exe
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes

[Files]
Source: "Release_Unica\IPTV_Studio_Pro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\IPTV Studio Pro"; Filename: "{app}\IPTV_Studio_Pro.exe"; IconFilename: "{app}\IPTV_Studio_Pro.exe"
Name: "{autodesktop}\IPTV Studio Pro"; Filename: "{app}\IPTV_Studio_Pro.exe"; IconFilename: "{app}\IPTV_Studio_Pro.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crea collegamento sul Desktop"; GroupDescription: "Collegamenti aggiuntivi:"; Flags: unchecked

[Run]
Filename: "{app}\IPTV_Studio_Pro.exe"; Description: "Avvia IPTV Studio Pro"; Flags: nowait postinstall skipifsilent
