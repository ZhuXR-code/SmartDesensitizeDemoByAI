; 敏感信息智能脱敏平台 - Windows 安装程序
; 使用 Inno Setup 编译：https://jrsoftware.org/isinfo.php
; 编译命令: iscc setup.iss

#define MyAppName "敏感信息智能脱敏平台"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Sensitive Data Protection Team"
#define MyAppURL "http://localhost:8080"
#define MyAppExeName "一键部署.bat"

[Setup]
AppId={{8A7E4F2C-3D5B-4A1E-9F6C-2D8E7A1B3C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\..\dist\installer
OutputBaseFilename={#MyAppName}_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\docker-deploy\docker.ico
UninstallDisplayName={#MyAppName}

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："; Flags: checkedonce

[Files]
; Docker 部署方案
Source: "..\docker-deploy\一键部署.bat"; DestDir: "{app}\docker-deploy"; Flags: ignoreversion
Source: "..\docker-deploy\deploy.sh"; DestDir: "{app}\docker-deploy"; Flags: ignoreversion
Source: "..\docker-deploy\docker-compose.yml"; DestDir: "{app}\docker-deploy"; Flags: ignoreversion
Source: "..\docker-deploy\Dockerfile.backend"; DestDir: "{app}\docker-deploy"; Flags: ignoreversion
Source: "..\docker-deploy\Dockerfile.frontend"; DestDir: "{app}\docker-deploy"; Flags: ignoreversion
Source: "..\docker-deploy\nginx.conf"; DestDir: "{app}\docker-deploy"; Flags: ignoreversion
Source: "..\docker-deploy\init_db.sql"; DestDir: "{app}\docker-deploy"; Flags: ignoreversion
Source: "..\docker-deploy\README.md"; DestDir: "{app}\docker-deploy"; Flags: ignoreversion

; 便携式部署方案
Source: "..\portable\启动平台.bat"; DestDir: "{app}\portable"; Flags: ignoreversion
Source: "..\portable\start.sh"; DestDir: "{app}\portable"; Flags: ignoreversion
Source: "..\portable\README.md"; DestDir: "{app}\portable"; Flags: ignoreversion
Source: "..\portable\backend\init_db.py"; DestDir: "{app}\portable\backend"; Flags: ignoreversion
Source: "..\portable\backend\requirements.txt"; DestDir: "{app}\portable\backend"; Flags: ignoreversion

; 文档
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\安装说明.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\部署说明.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\windows-installer\README.md"; DestDir: "{app}\windows-installer"; Flags: ignoreversion
Source: "..\windows-installer\build_installer.bat"; DestDir: "{app}\windows-installer"; Flags: ignoreversion
Source: "..\windows-installer\launcher.py"; DestDir: "{app}\windows-installer"; Flags: ignoreversion

; 卸载脚本
Source: "uninstall_script.bat"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\data"; Permissions: users-full
Name: "{app}\uploads"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full

[Icons]
Name: "{group}\一键启动（Docker部署）"; Filename: "{app}\docker-deploy\一键部署.bat"; WorkingDir: "{app}\docker-deploy"; Comment: "使用 Docker 一键部署平台（需先安装 Docker Desktop）"
Name: "{group}\便携式启动（Python）"; Filename: "{app}\portable\启动平台.bat"; WorkingDir: "{app}\portable"; Comment: "使用 Python 便携式启动（需先安装 Python 3.10+）"
Name: "{group}\安装说明"; Filename: "{app}\安装说明.md"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\docker-deploy\{#MyAppExeName}"; WorkingDir: "{app}\docker-deploy"; Tasks: desktopicon; Comment: "一键启动敏感信息智能脱敏平台"

[Run]
Filename: "{app}\安装说明.md"; Description: "查看安装说明"; Flags: postinstall nowait shellexec skipifsilent unchecked
Filename: "{app}\docker-deploy\一键部署.bat"; Description: "启动 Docker 部署"; Flags: postinstall nowait skipifsilent unchecked

[UninstallRun]
Filename: "{app}\uninstall_script.bat"; Flags: runhidden

[Code]
function IsDockerInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Exec('cmd.exe', '/C docker --version >nul 2>&1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := (ResultCode = 0);
end;

function IsPythonInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Exec('cmd.exe', '/C python --version >nul 2>&1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := (ResultCode = 0);
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    if not IsDockerInstalled then
    begin
      SuppressibleMsgBox(
        '提示：未检测到 Docker Desktop。' + #13#10 +
        'Docker 部署方案需要先安装 Docker Desktop。' + #13#10#13#10 +
        '如果您选择便携式部署，请确保已安装 Python 3.10+。' + #13#10#13#10 +
        'Docker 下载地址：https://www.docker.com/products/docker-desktop/',
        mbInformation, MB_OK, IDOK
      );
    end;
  end;
end;
