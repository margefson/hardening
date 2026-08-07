# Lab 06B - Auditoria de Privilegios Windows (somente leitura)
$ErrorActionPreference = "Continue"
$Out = "d:\MMB\workspace\hardening\lab06a\..\lab06b\evidencias"
$Out = "d:\MMB\workspace\hardening\lab06b\evidencias"
$Shot = Join-Path $Out "shots"
$Raw = Join-Path $Out "raw"
New-Item -ItemType Directory -Force -Path $Shot, $Raw | Out-Null

function Save-Shot($name, [scriptblock]$sb) {
  $path = Join-Path $Shot "$name.txt"
  $content = & $sb 2>&1 | Out-String
  Set-Content -Path $path -Value $content -Encoding UTF8
  Write-Host "OK $name"
}

Save-Shot "01_ambiente" {
  "PS> hostname; whoami; Get-Date"
  hostname
  whoami
  Get-Date
  $os = Get-CimInstance Win32_OperatingSystem
  "OS: $($os.Caption) | Version: $($os.Version) | Build: $($os.BuildNumber)"
  "Estacao: WIN-ADM-01 (MachadoPC) | Lab 06B - Privilegios"
}

Save-Shot "02_whoami_priv" {
  "PS> whoami /priv"
  whoami /priv
  ""
  "PS> # Contagem"
  $lines = (whoami /priv) | Where-Object { $_ -match "Privilege|Se[A-Z]" -or $_ -match "Habilitad|Desabilit|Enabled|Disabled" }
}

Save-Shot "03_user_rights_secedit" {
  "PS> # Equivalente a secpol.msc > User Rights Assignment (export secedit)"
  $cfg = Join-Path $env:TEMP "lab06b_secedit.inf"
  secedit /export /cfg $cfg /areas USER_RIGHTS 2>&1
  "Exported: $cfg"
  ""
  if (Test-Path $cfg) {
    "PS> Get-Content secedit USER_RIGHTS (amostra privilegios criticos)"
    Get-Content $cfg | Where-Object {
      $_ -match "^(Se|\[)" -and $_ -notmatch "^;"
    } | Select-Object -First 80
    ""
    "PS> Privilegios sensiveis (filtrados)"
    Get-Content $cfg | Where-Object {
      $_ -match "Se(Debug|TakeOwnership|Backup|Restore|LoadDriver|Tcb|Impersonate|AssignPrimaryToken|Shutdown|RemoteInteractive|Interactive|Deny)"
    }
  }
}

Save-Shot "04_gpedit_status" {
  "PS> # gpedit.msc / secpol.msc disponibilidade nesta edicao"
  $gpedit = Test-Path "$env:SystemRoot\System32\gpedit.msc"
  $secpol = Test-Path "$env:SystemRoot\System32\secpol.msc"
  "gpedit.msc presente: $gpedit"
  "secpol.msc presente: $secpol"
  ""
  "PS> Get-CimInstance Win32_OperatingSystem | Select Caption, OSArchitecture"
  Get-CimInstance Win32_OperatingSystem | Select-Object Caption, OSArchitecture, Version | Format-List | Out-String
  ""
  "# Windows 11 Home: gpedit/secpol podem estar ausentes."
  "# Evidencia alternativa: secedit /export USER_RIGHTS (shot 03) + whoami /priv."
  "# Politicas locais relevantes ao privilegio: UAC, User Rights, Audit Policy."
  ""
  "PS> Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System | Select EnableLUA, ConsentPromptBehaviorAdmin, FilterAdministratorToken"
  Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" |
    Select-Object EnableLUA, ConsentPromptBehaviorAdmin, ConsentPromptBehaviorUser, FilterAdministratorToken, PromptOnSecureDesktop |
    Format-List | Out-String
}

Save-Shot "05_whoami_all" {
  "PS> whoami /all"
  whoami /all
}

Save-Shot "06_powershell_security" {
  "PS> Get-Command *Security* | Measure-Object"
  $cmds = Get-Command *Security* -ErrorAction SilentlyContinue
  "Total cmdlets/funcoes *Security*: $($cmds.Count)"
  ""
  "PS> Get-Command *Security* | Select-Object -First 25 Name, CommandType, Source"
  $cmds | Select-Object -First 25 Name, CommandType, Source | Format-Table -AutoSize | Out-String
  ""
  "PS> Get-LocalGroupMember -Group Administradores"
  Get-LocalGroupMember -Group "Administradores" | Format-Table Name, ObjectClass, PrincipalSource -AutoSize | Out-String
  ""
  "PS> whoami /groups | findstr /i Administr"
  whoami /groups | findstr /i "Administr"
}

Save-Shot "07_mmc_equiv" {
  "PS> # MMC: centraliza snap-ins (Local Security Policy, Event Viewer, etc.)"
  "PS> where.exe mmc"
  where.exe mmc 2>&1
  "PS> Test-Path mmc.exe / secpol / eventvwr"
  "mmc: $(Test-Path $env:SystemRoot\System32\mmc.exe)"
  "eventvwr.msc: $(Test-Path $env:SystemRoot\System32\eventvwr.msc)"
  "secpol.msc: $(Test-Path $env:SystemRoot\System32\secpol.msc)"
  ""
  "# Snap-ins tipicos para auditoria de privilegios:"
  "# - Security Templates / Local Security Policy (User Rights Assignment)"
  "# - Event Viewer (Security log)"
  "# - Computer Management (Local Users and Groups)"
  "# Evidencia obtida via secedit + whoami + Get-WinEvent (sem alterar config)."
}

Save-Shot "08_event_viewer" {
  "PS> # Equivalente eventvwr.msc - logs de Seguranca / Sistema"
  "PS> Get-WinEvent -ListLog Security, System, Application | Select LogName, RecordCount, IsEnabled"
  Get-WinEvent -ListLog Security, System, Application -ErrorAction SilentlyContinue |
    Select-Object LogName, RecordCount, IsEnabled | Format-Table -AutoSize | Out-String
  ""
  "PS> Get-WinEvent -LogName Security -MaxEvents 8 -ErrorAction SilentlyContinue | Format-Table TimeCreated, Id, LevelDisplayName, Message -Wrap"
  try {
    Get-WinEvent -LogName Security -MaxEvents 8 -ErrorAction Stop |
      Select-Object TimeCreated, Id, ProviderName |
      Format-Table -AutoSize | Out-String
  } catch {
    "Security log: acesso limitado ou vazio ($($_.Exception.Message))"
    "PS> Get-WinEvent -LogName System -MaxEvents 8 | Select TimeCreated, Id, ProviderName"
    Get-WinEvent -LogName System -MaxEvents 8 |
      Select-Object TimeCreated, Id, ProviderName |
      Format-Table -AutoSize | Out-String
  }
  ""
  "# Categorias tipicas no Event Viewer: Application, Security, Setup, System, Forwarded Events"
  "# Log Security registra logon, privilegio especial usado (4672), mudancas de politica, etc."
}

Save-Shot "09_consolidacao" {
  "=== CONSOLIDACAO AUDITORIA PRIVILEGIOS LAB 06B ==="
  "Estacao: WIN-ADM-01 / MachadoPC"
  "Usuario sessao: $(whoami)"
  ""
  "1) Token (whoami /priv) - privilegios ENABLED:"
  whoami /priv | Select-String "Enabled|Habilitado"
  ""
  "2) Membros Administradores:"
  (Get-LocalGroupMember -Group "Administradores" | ForEach-Object Name) -join ", "
  ""
  "3) UAC EnableLUA:"
  (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System").EnableLUA
  ""
  "4) Inconsistencias vs menor privilegio:"
  "- Conta diaria marge pertence a Administradores (Lab 06A)"
  "- Token filtrado UAC reduz privilegios na sessao media, mas elevacao permanece disponivel"
  "- Conta postgres habilitada (servico) - revisar direitos de logon"
  ""
  "5) Recomendacoes: conta admin separada; JIT; revisar User Rights; auditar 4672; Lab 06C NTFS"
}

Get-ChildItem $Shot -Filter "*.txt" | Sort-Object Name | ForEach-Object {
  "===== $($_.Name) ====="
  Get-Content $_.FullName -Raw
  ""
} | Set-Content (Join-Path $Raw "lab06b_full.txt") -Encoding UTF8

Write-Host "CAPTURE DONE"
Get-ChildItem $Shot | Select-Object Name, Length
