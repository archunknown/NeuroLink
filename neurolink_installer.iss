[Setup]
AppName=NeuroLink
AppVersion=1.0
DefaultDirName={autopf}\NeuroLink
DefaultGroupName=NeuroLink
OutputDir=installer
OutputBaseFilename=NeuroLink_Setup
SetupIconFile=app\assets\logo.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\NeuroLink\NeuroLink.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\NeuroLink\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NeuroLink"; Filename: "{app}\NeuroLink.exe"
Name: "{autodesktop}\NeuroLink"; Filename: "{app}\NeuroLink.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
