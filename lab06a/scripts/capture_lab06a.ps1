# Lab 06A - Auditoria de Identidades Windows (somente leitura)
$ErrorActionPreference = "Continue"
$Out = "d:\MMB\workspace\hardening\lab06a\evidencias"
$Shot = Join-Path $Out "shots"
$Raw = Join-Path $Out "raw"
New-Item -ItemType Directory -Force -Path $Shot, $Raw | Out-Null

function Save-Shot($name, $scriptBlock) {
  $path = Join-Path $Shot "$name.txt"
  $content = & $scriptBlock 2>&1 | Out-String
  Set-Content -Path $path -Value $content -Encoding UTF8
  Write-Host "OK $name"
}

Save-Shot "01_ambiente" {
  "PS> hostname; whoami; Get-Date"
  hostname
  whoami
  Get-Date
  "PS> systeminfo | Select-String 'OS Name','OS Version','System Type'"
  systeminfo | Select-String "OS Name","OS Version","System Type"
}

Save-Shot "02_whoami" {
  "PS> whoami"
  whoami
  ""
  "# Ex1: usuario autenticado; conta local vs dominio; base da autorizacao"
}

Save-Shot "03_whoami_user" {
  "PS> whoami /user"
  whoami /user
  ""
  "# Ex2: SID permanente - Windows autoriza por SID, nao pelo nome"
}

Save-Shot "04_whoami_groups" {
  "PS> whoami /groups"
  whoami /groups
}

Save-Shot "05_net_user" {
  "PS> net user"
  net user
  ""
  $users = (Get-LocalUser).Name
  "PS> # Detalhe de contas locais (amostra)"
  foreach ($u in $users) {
    "----- net user $u -----"
    net user $u
    ""
  }
}

Save-Shot "06_net_localgroup" {
  "PS> net localgroup"
  net localgroup
  ""
  "PS> net localgroup Administrators"
  net localgroup Administrators
  ""
  # Portuguese locale may use Administradores
  "PS> net localgroup Administradores"
  net localgroup Administradores 2>&1
  ""
  "PS> net localgroup Users"
  net localgroup Users 2>&1
  "PS> net localgroup Usuarios"
  net localgroup Usuarios 2>&1
}

Save-Shot "07_lusrmgr_equiv" {
  "PS> # Equivalente documental a lusrmgr.msc (auditoria grafica)"
  "PS> Get-LocalUser | Format-Table Name, Enabled, Description, LastLogon -AutoSize"
  Get-LocalUser | Format-Table Name, Enabled, Description, LastLogon -AutoSize | Out-String
  ""
  "PS> Get-LocalGroup | Format-Table Name, Description -AutoSize"
  Get-LocalGroup | Format-Table Name, Description -AutoSize | Out-String
  ""
  "PS> Get-LocalGroupMember -Group Administrators | Format-Table Name, ObjectClass, PrincipalSource -AutoSize"
  try {
    Get-LocalGroupMember -Group "Administrators" | Format-Table Name, ObjectClass, PrincipalSource -AutoSize | Out-String
  } catch {
    Get-LocalGroupMember -Group "Administradores" | Format-Table Name, ObjectClass, PrincipalSource -AutoSize | Out-String
  }
}

Save-Shot "08_get_localuser" {
  "PS> Get-LocalUser | Format-List Name, Enabled, Description, SID, PasswordRequired, UserMayChangePassword, PasswordExpires, LastLogon"
  Get-LocalUser | Format-List Name, Enabled, Description, SID, PasswordRequired, UserMayChangePassword, PasswordExpires, LastLogon | Out-String
}

Save-Shot "09_whoami_all" {
  "PS> whoami /all"
  whoami /all
}

# Raw consolidado
Get-ChildItem $Shot -Filter "*.txt" | Sort-Object Name | ForEach-Object {
  "===== $($_.Name) ====="
  Get-Content $_.FullName -Raw
  ""
} | Set-Content (Join-Path $Raw "lab06a_full.txt") -Encoding UTF8

Write-Host "CAPTURE DONE -> $Shot"
Get-ChildItem $Shot | Select-Object Name, Length
