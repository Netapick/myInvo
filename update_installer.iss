[Setup]
; Installateur de mise à jour myInvo - Ne remplace que l'exécutable
AppId={{C7F2E8A1-9B3D-4E6F-8A2C-1D5E3F7B9C4E}
AppName=myInvo - Mise à jour
AppVersion=1.4.1
AppVerName=myInvo 1.4.1 - Mise à jour
AppPublisher=Julien Gataleta
DefaultDirName={autopf}\myInvo
DisableDirPage=no
DisableWelcomePage=no
DisableFinishedPage=no
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=myInvo-1.4.1-Update
SetupIconFile=myinvo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UpdateUninstallLogAppName=no

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Seul le fichier exécutable est remplacé
Source: "dist\myInvo.exe"; DestDir: "{app}"; Flags: ignoreversion

[Messages]
french.WelcomeLabel2=Cet assistant va installer la mise à jour sur votre ordinateur.%n%nIl est recommandé de fermer toutes les autres applications avant de continuer.
french.FinishedLabel=La mise à jour a été installée avec succès. L'application peut maintenant être relancée.

[Code]
function InitializeSetup(): Boolean;
var
  InstallPath: string;
begin
  // Vérifier que myInvo est déjà installé
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{C7F2E8A1-9B3D-4E6F-8A2C-1D5E3F7B9C4E}_is1', 'InstallLocation', InstallPath) or
     RegQueryStringValue(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{C7F2E8A1-9B3D-4E6F-8A2C-1D5E3F7B9C4E}_is1', 'InstallLocation', InstallPath) then
  begin
    // myInvo est installé, procéder à la mise à jour
    Result := True;
  end
  else
  begin
    MsgBox('myInvo doit être installé avant d''appliquer cette mise à jour.' + #13#10 + 
           'Veuillez installer myInvo en premier.', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Message de confirmation
    MsgBox('Mise à jour installée avec succès!' + #13#10 + 
           'Vous pouvez maintenant relancer myInvo.', mbInformation, MB_OK);
  end;
end;