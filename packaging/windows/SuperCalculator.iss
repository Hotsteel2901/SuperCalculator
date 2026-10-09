#define AppName "SuperCalculator - Next Era"
#define AppVersion "0.1.0"
#define AppPublisher "SuperCalculator maintainers"
#define AppExeName "supercalculator_next_era.exe"
#ifndef BuildDir
  #define BuildDir "..\\..\\flutter\\build\\windows\\x64\\runner\\Release"
#endif

[Setup]
AppId={{B7E6C9A4-4E77-4A1F-9D93-7E8A3A9E2A11}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\SuperCalculator Next Era
DefaultGroupName={#AppName}
OutputDir=Output
OutputBaseFilename=SuperCalculator-Next-Era-windows-x64-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExeName}

[Files]
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
