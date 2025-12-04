[Setup]
; Script généré par Inno Setup pour myInvo v1.4.1
; NOTE: La valeur de AppId identifie de manière unique cette application.
; Ne pas utiliser la même valeur AppId dans les installeurs pour d'autres applications.
;
; NOUVEAUTÉS VERSION 1.4.1:
; - Sécurisation du système de licence renforcée
; - Validation stricte des informations utilisateur avec la clé
; - Empêche l'activation de clés avec des informations incorrectes
; - Système de mise à jour offline complet (Python, Batch, Inno Setup)
; - Gestion automatique des versions depuis version_info.txt
; - Correction de la validation des licences avec informations utilisateur
AppId={{C7F2E8A1-9B3D-4E6F-8A2C-1D5E3F7B9C4E}
AppName=myInvo
AppVersion=1.4.1
AppVerName=myInvo 1.4.1
AppPublisher=Julien Gataleta
DefaultDirName={autopf}\myInvo
DefaultGroupName=myInvo
DisableDirPage=no
AllowNoIcons=yes
LicenseFile=LICENCE
InfoBeforeFile=README.txt
OutputDir=installer
OutputBaseFilename=myInvo-1.4.1
SetupIconFile=myinvo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\myInvo.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENCE"; DestDir: "{app}"; Flags: ignoreversion
Source: "myinvo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "version_info.txt"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: N'utilisez pas "Flags: ignoreversion" sur les fichiers système

[Icons]
Name: "{group}\myInvo"; Filename: "{app}\myInvo.exe"; IconFilename: "{app}\myinvo.ico"
Name: "{group}\Guide d'utilisation"; Filename: "{app}\README.txt"
Name: "{group}\Licence"; Filename: "{app}\LICENCE"
Name: "{group}\{cm:UninstallProgram,myInvo}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\myInvo"; Filename: "{app}\myInvo.exe"; Tasks: desktopicon; IconFilename: "{app}\myinvo.ico"

[Run]
Filename: "{app}\myInvo.exe"; Description: "{cm:LaunchProgram,myInvo}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Supprimer tous les dossiers de données utilisateur lors de la désinstallation
Type: filesandordirs; Name: "{app}\config"
Type: filesandordirs; Name: "{app}\devis"
Type: filesandordirs; Name: "{app}\factures"
Type: filesandordirs; Name: "{app}\archives"
Type: filesandordirs; Name: "{app}\logs"


[Registry]
; Associations de fichiers pour les archives myInvo (optionnel)
Root: HKCU; Subkey: "Software\Classes\.myinvo"; ValueType: string; ValueName: ""; ValueData: "myInvoArchive"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\myInvoArchive"; ValueType: string; ValueName: ""; ValueData: "Archive myInvo"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\myInvoArchive\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\myinvo.ico"
Root: HKCU; Subkey: "Software\Classes\myInvoArchive\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\myInvo.exe"" ""%1"""

[CustomMessages]
french.LaunchProgram=Lancer %1
french.CreateDesktopIcon=Créer une icône sur le &bureau
french.AdditionalIcons=Icônes supplémentaires:
french.UninstallProgram=Désinstaller %1

[Code]

function InitializeSetup(): Boolean;
begin
  // Vérifier la version de Windows (Windows 10 minimum recommandé)
  if not IsWin64 then
  begin
    MsgBox('myInvo nécessite Windows 64-bit pour fonctionner correctement.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Les fichiers seront vérifiés automatiquement par Inno Setup
  
  Result := True;
end;

procedure InitializeWizard();
begin
  // Installation directe sans demande de clé
  // L'activation se fera via l'interface de l'application
end;



function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  // Installation simplifiée sans validation de clé
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  UserInfoFile: string;
  UserInfoData: string;
  RegistryData: string;
  RegistryFile: string;
begin
  if CurStep = ssPostInstall then
  begin
    // Créer les dossiers de travail lors de l'installation
    if not DirExists(ExpandConstant('{app}\config')) then
      CreateDir(ExpandConstant('{app}\config'));
    if not DirExists(ExpandConstant('{app}\devis')) then
      CreateDir(ExpandConstant('{app}\devis'));
    if not DirExists(ExpandConstant('{app}\factures')) then
      CreateDir(ExpandConstant('{app}\factures'));
    if not DirExists(ExpandConstant('{app}\archives')) then
      CreateDir(ExpandConstant('{app}\archives'));
    if not DirExists(ExpandConstant('{app}\logs')) then
      CreateDir(ExpandConstant('{app}\logs'));
    
    // Créer le fichier d'informations utilisateur avec valeurs par défaut
    UserInfoFile := ExpandConstant('{app}\config\user_info.json');
    UserInfoData := '{' + #13#10 +
      '  "user_name": "Utilisateur",' + #13#10 +
      '  "company": "Entreprise",' + #13#10 +
      '  "install_date": "' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0) + '"' + #13#10 +
      '}';
    SaveStringToFile(UserInfoFile, UserInfoData, False);
    
    // Créer un registre de licence initial (chiffré)
    RegistryFile := ExpandConstant('{app}\.key_registry.json');
    RegistryData := '{' + #13#10 +
      '  "encrypted": "Z0FBQUFBQnBMMGtKVGJHeDRXYlBPX2F6Q1pabTVCZ1dvS0h4MVJzRGxqWGVWSjByUzVLQ3ZmYlhMZl9nej",' + #13#10 +
      '  "version": "2.0c"' + #13#10 +
      '}';
    SaveStringToFile(RegistryFile, RegistryData, False);
    
    // Note: La clé de licence ne sera pas sauvegardée automatiquement
    // L'utilisateur devra l'activer manuellement via l'interface de l'application
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usUninstall:
      begin
        // Supprimer automatiquement tous les dossiers de données lors de la désinstallation
        if DirExists(ExpandConstant('{app}\config')) then
          DelTree(ExpandConstant('{app}\config'), True, True, True);
        if DirExists(ExpandConstant('{app}\devis')) then
          DelTree(ExpandConstant('{app}\devis'), True, True, True);
        if DirExists(ExpandConstant('{app}\factures')) then
          DelTree(ExpandConstant('{app}\factures'), True, True, True);
        if DirExists(ExpandConstant('{app}\archives')) then
          DelTree(ExpandConstant('{app}\archives'), True, True, True);
        if DirExists(ExpandConstant('{app}\logs')) then
          DelTree(ExpandConstant('{app}\logs'), True, True, True);
      end;
  end;
end;