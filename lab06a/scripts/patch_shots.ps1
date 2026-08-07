$os = Get-CimInstance Win32_OperatingSystem
$g = Get-LocalGroupMember -Group "Administradores"
$u = Get-LocalUser
$shot = "d:\MMB\workspace\hardening\lab06a\evidencias\shots"

@(
  "OS=$($os.Caption)"
  "Version=$($os.Version)"
  "Build=$($os.BuildNumber)"
  "UsersTotal=$($u.Count)"
  "Enabled=$(($u | Where-Object Enabled | ForEach-Object Name) -join ',')"
  "Disabled=$(($u | Where-Object { -not $_.Enabled } | ForEach-Object Name) -join ',')"
  "Admins=$(($g | ForEach-Object Name) -join ',')"
) | Set-Content (Join-Path $shot "_summary.txt") -Encoding UTF8

$envBlock = @"
PS> hostname; whoami; Get-Date
$(hostname)
$(whoami)
$(Get-Date)
PS> Get-CimInstance Win32_OperatingSystem | Select Caption, Version, BuildNumber
$($os.Caption)
Version: $($os.Version)  Build: $($os.BuildNumber)
System Type: $((Get-CimInstance Win32_ComputerSystem).SystemType)
"@
Set-Content (Join-Path $shot "01_ambiente.txt") -Value $envBlock -Encoding UTF8

$extra = @"

PS> Get-LocalGroupMember -Group Administradores | Format-Table Name, ObjectClass, PrincipalSource -AutoSize
$($g | Format-Table Name, ObjectClass, PrincipalSource -AutoSize | Out-String)
"@
Add-Content (Join-Path $shot "07_lusrmgr_equiv.txt") -Value $extra -Encoding UTF8

# Usuarios group
$grpUsers = net localgroup "Usuários" 2>&1 | Out-String
Add-Content (Join-Path $shot "06_net_localgroup.txt") -Value ("`nPS> net localgroup Usuarios`n" + $grpUsers) -Encoding UTF8

Get-Content (Join-Path $shot "_summary.txt")
Write-Host "PATCH OK"
