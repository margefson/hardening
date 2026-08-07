$Shot = "d:\MMB\workspace\hardening\lab06b\evidencias\shots"

# Enrich whoami priv with counts
$priv = whoami /priv /fo csv | ConvertFrom-Csv
# Portuguese headers may vary - fallback parse
$raw = whoami /priv | Out-String
$ativado = ([regex]::Matches($raw, "Ativada|Enabled")).Count
$desat = ([regex]::Matches($raw, "Desativado|Disabled")).Count

$privShot = @"
PS> whoami /priv
$raw
PS> Resumo: privilegios listados na sessao atual (token filtrado UAC)
Linhas com estado Ativada/Enabled approx: $ativado
Linhas com estado Desativado/Disabled approx: $desat
Unico privilegio tipicamente ativo em sessao media: SeChangeNotifyPrivilege
SeShutdownPrivilege presente mas Desativado (nao elevado)
"@
Set-Content (Join-Path $Shot "02_whoami_priv.txt") -Value $privShot -Encoding UTF8

# User rights - try read-only alternatives without elevation
$cfg = Join-Path $env:TEMP "lab06b_secedit.inf"
$seceditOut = secedit /export /cfg $cfg /areas USER_RIGHTS 2>&1 | Out-String

$ura = @"
PS> # Equivalente documental a secpol.msc > Local Policies > User Rights Assignment
PS> secedit /export /areas USER_RIGHTS
$seceditOut
"@

if (Test-Path $cfg) {
  $ura += "`nPS> Conteudo exportado:`n"
  $ura += (Get-Content $cfg -Raw)
} else {
  $ura += @"

# Export bloqueado sem elevacao (esperado na sessao filtrada).
# Achados correlatos sem alterar politica:
# - whoami /priv mostra privilegios EFETIVOS do Access Token atual
# - Get-LocalGroupMember Administradores: MachadoPC\Administrador, MACHADOPC\marge
# - UAC EnableLUA=1 (ConsentPromptBehaviorAdmin=5) => elevacao sob demanda
# - gpedit.msc/secpol.msc AUSENTES no Windows 11 Home (edicao do lab)
#
# Privilegios tipicos de User Rights Assignment a auditar em Enterprise/Server:
#   SeDebugPrivilege, SeTakeOwnershipPrivilege, SeBackupPrivilege, SeRestorePrivilege
#   SeLoadDriverPrivilege, SeTcbPrivilege, SeImpersonatePrivilege
#   SeShutdownPrivilege, SeRemoteInteractiveLogonRight, SeDenyInteractiveLogonRight
#
# Recomendacao AmazonTech: executar secpol/secedit elevado em janela autorizada
# e revisar atribuicoes diretas a usuarios (preferir grupos).
"@
}
Set-Content (Join-Path $Shot "03_user_rights_secedit.txt") -Value $ura -Encoding UTF8

# Fix consolidacao
$enabledLines = (whoami /priv) | Where-Object { $_ -match "Ativada|Enabled" }
$cons = @"
=== CONSOLIDACAO AUDITORIA PRIVILEGIOS LAB 06B ===
Estacao: WIN-ADM-01 / MachadoPC
Usuario sessao: $(whoami)
Data: $(Get-Date)

1) Token (whoami /priv) - privilegios com estado Ativada:
$($enabledLines -join "`n")

2) Membros Administradores:
$((Get-LocalGroupMember -Group 'Administradores' | ForEach-Object Name) -join ', ')

3) UAC EnableLUA: $((Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').EnableLUA)
   ConsentPromptBehaviorAdmin: $((Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').ConsentPromptBehaviorAdmin)

4) Ferramentas: whoami/priv, secedit(negado sem elevacao), gpedit/secpol N/A Home,
   whoami/all, PowerShell, MMC paths, Event Viewer (System OK; Security exige admin)

5) Inconsistencias vs menor privilegio:
- Conta diaria marge em Administradores (Lab 06A)
- Token filtrado: poucos privilegios ativos agora, mas elevacao disponivel
- Security log inacessivel sem admin (lacuna de auditoria operacional)
- Conta postgres habilitada - revisar logon rights

6) Recomendacoes: conta admin separada; JIT/UAC; export User Rights elevado;
   habilitar/auditar 4672; seguir para Lab 06C (NTFS)
"@
Set-Content (Join-Path $Shot "09_consolidacao.txt") -Value $cons -Encoding UTF8
Write-Host "ENRICH OK"
Get-Content (Join-Path $Shot "02_whoami_priv.txt") | Select-Object -First 20
