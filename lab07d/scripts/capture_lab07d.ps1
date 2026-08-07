# Lab 07D - Administracao Segura com PowerShell (somente consulta)
$ErrorActionPreference = "Continue"
$Base = "d:\MMB\workspace\hardening\lab07d"
$Shot = Join-Path $Base "evidencias\shots"
$Raw = Join-Path $Base "evidencias\raw"
$Docs = Join-Path $Base "evidencias\docs"
New-Item -ItemType Directory -Force -Path $Shot, $Raw, $Docs | Out-Null

function Save-Shot($name, [scriptblock]$sb) {
  Set-Content -Path (Join-Path $Shot "$name.txt") -Value ((& $sb 2>&1 | Out-String)) -Encoding UTF8
  Write-Host "OK $name"
}

Save-Shot "01_ambiente" {
  "PS> hostname; whoami; Get-Date"
  hostname; whoami; Get-Date
  $os = Get-CimInstance Win32_OperatingSystem
  "OS: $($os.Caption) | Version: $($os.Version) | Build: $($os.BuildNumber)"
  "Estacao: WIN-ADM-01 | Lab 07D - Administracao Segura com PowerShell"
  "Escopo: explorar plataforma PS (sem alterar Execution Policy / configs)"
}

Save-Shot "02_versao_powershell" {
  "PS> # Atividade 1 - Ambiente PowerShell / Terminal"
  "PS> $PSVersionTable"
  $PSVersionTable | Format-List | Out-String
  ""
  "PS> $Host.Name; $Host.Version; $Host.UI.RawUI.WindowTitle"
  "Host.Name: $($Host.Name)"
  "Host.Version: $($Host.Version)"
  "Edition: $($PSVersionTable.PSEdition)"
  "CompatibleVersions: $($PSVersionTable.PSCompatibleVersions -join ', ')"
  ""
  "Windows Terminal disponivel:"
  $wt = Get-Command wt.exe -ErrorAction SilentlyContinue
  "wt.exe no PATH: $($null -ne $wt)"
  if ($wt) { "wt path: $($wt.Source)" }
  "powershell.exe: $((Get-Command powershell.exe).Source)"
  $pwsh = Get-Command pwsh.exe -ErrorAction SilentlyContinue
  "pwsh.exe (PS Core): $($null -ne $pwsh)"
  if ($pwsh) { "pwsh: $($pwsh.Source) | $(& pwsh -NoProfile -Command '$PSVersionTable.PSVersion')" }
}

Save-Shot "03_ajuda_comandos" {
  "PS> # Atividade 2 - Recursos de ajuda / documentacao"
  "PS> Get-Help Get-Service"
  Get-Help Get-Service | Select-Object Name, Synopsis, Category, ModuleName |
    Format-List | Out-String
  "--- Synopsis / Description (resumo) ---"
  (Get-Help Get-Service).Synopsis
  ""
  "Finalidade Get-Help: documentacao integrada (synopsis, parametros, exemplos)."
  ""
  "PS> Get-Command | Measure-Object"
  $gc = Get-Command
  "Total de comandos visiveis nesta sessao: $($gc.Count)"
  "Por CommandType:"
  $gc | Group-Object CommandType | Sort-Object Count -Descending |
    Select-Object Name, Count | Format-Table -AutoSize | Out-String
  ""
  "PS> Get-Command -CommandType Cmdlet | Select -First 12 Name, Source"
  Get-Command -CommandType Cmdlet |
    Select-Object -First 12 Name, Source |
    Format-Table -AutoSize | Out-String
  "Finalidade Get-Command: inventariar cmdlets/funcoes/alias disponiveis para admin."
}

Save-Shot "04_servicos_processos" {
  "PS> # Atividade 3 - Get-Service / Get-Process (amostra)"
  "PS> Get-Service | Where-Object Status -eq 'Running' | Select -First 15"
  Get-Service | Where-Object { $_.Status -eq 'Running' } |
    Select-Object -First 15 Name, Status, StartType |
    Format-Table -AutoSize | Out-String
  ""
  "Servicos relevantes AmazonTech (Defender/Firewall/BitLocker):"
  Get-Service WinDefend, MpsSvc, BDESVC, EventLog, Schedule -ErrorAction SilentlyContinue |
    Format-Table Name, Status, StartType -AutoSize | Out-String
  ""
  "PS> Get-Process | Sort-Object CPU -Descending | Select -First 12"
  Get-Process | Sort-Object CPU -Descending |
    Select-Object -First 12 ProcessName, Id, CPU, @{N='WS_MB';E={[math]::Round($_.WorkingSet64/1MB,1)}} |
    Format-Table -AutoSize | Out-String
  ""
  "Observacao: amostras para auditoria operacional; nao alteram estado do sistema."
}

Save-Shot "05_execution_policy" {
  "PS> # Atividade 4 - Execution Policy (somente leitura)"
  "PS> Get-ExecutionPolicy"
  Get-ExecutionPolicy
  ""
  "PS> Get-ExecutionPolicy -List"
  Get-ExecutionPolicy -List | Format-Table -AutoSize | Out-String
  ""
  "Finalidade: controlar quais scripts podem ser executados (Restricted,"
  "AllSigned, RemoteSigned, Unrestricted, Bypass, Undefined)."
  "Governanca AmazonTech: preferir RemoteSigned ou AllSigned + assinatura de codigo;"
  "evitar Bypass permanente; alteracoes so via change control."
  "Nenhuma politica foi alterada nesta atividade (Set-ExecutionPolicy NAO executado)."
}

Save-Shot "06_computerinfo" {
  "PS> # Atividade 5a - Get-ComputerInfo (sistema operacional)"
  "PS> Get-ComputerInfo | Select OsName, OsVersion, OsBuildNumber, OsArchitecture, CsName, CsDomain, WindowsProductName, WindowsInstallationType, BiosFirmwareType, HyperVisorPresent"
  Get-ComputerInfo |
    Select-Object OsName, OsVersion, OsBuildNumber, OsArchitecture, CsName, CsDomain,
      WindowsProductName, WindowsInstallationType, BiosFirmwareType, HyperVisorPresent,
      OsInstallDate, OsLastBootUpTime |
    Format-List | Out-String
}

Save-Shot "07_integracao_labs" {
  "PS> # Atividade 5b - Integracao com Labs 07A/07B (consulta)"
  "PS> Get-MpComputerStatus | Select AntivirusEnabled, RealTimeProtectionEnabled, AMServiceEnabled, AntivirusSignatureVersion, NISEnabled"
  try {
    Get-MpComputerStatus |
      Select-Object AntivirusEnabled, RealTimeProtectionEnabled, AMServiceEnabled,
        AntivirusSignatureVersion, NISEnabled, IsTamperProtected |
      Format-List | Out-String
  } catch { "Get-MpComputerStatus: $($_.Exception.Message)" }
  ""
  "PS> Get-NetFirewallProfile | Select Name, Enabled, DefaultInboundAction, DefaultOutboundAction"
  Get-NetFirewallProfile |
    Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction |
    Format-Table -AutoSize | Out-String
  ""
  "Integracao: o mesmo shell consulta Defender (07A), Firewall (07B) e info do SO,"
  "permitindo auditoria padronizada, scripts versionados e evidencias auditaveis"
  "sem depender apenas da GUI de cada console (wf.msc, Windows Security, etc.)."
}

Save-Shot "08_consolidacao" {
  "PS> # Consolidacao Lab 07D - governanca PowerShell AmazonTech"
  "PSVersion: $($PSVersionTable.PSVersion) | Edition: $($PSVersionTable.PSEdition)"
  "ExecutionPolicy efetiva: $(Get-ExecutionPolicy)"
  "Escopos:"
  Get-ExecutionPolicy -List | ForEach-Object { "  $($_.Scope)=$($_.ExecutionPolicy)" }
  "Host: $($Host.Name)"
  "Comandos visiveis: $((Get-Command | Measure-Object).Count)"
  "Windows Terminal: $([bool](Get-Command wt.exe -EA SilentlyContinue))"
  ""
  "Parecer preliminar:"
  "PowerShell ATENDE como plataforma de administracao segura para consulta/auditoria."
  "Proximo passo corporativo: baseline de Execution Policy, logging (ScriptBlock),"
  "modulos assinados, Just Enough Administration (JEA) e repositorio de scripts."
  "Nenhuma configuracao permanente foi alterada nesta OS."
}

@"
=== Lab 07D raw dump $(Get-Date) ===
PSVersion=$($PSVersionTable.PSVersion)
ExecutionPolicy=$(Get-ExecutionPolicy)
$((Get-ExecutionPolicy -List | Format-Table | Out-String))
"@ | Set-Content -Path (Join-Path $Raw "lab07d_full.txt") -Encoding UTF8

@"
Lab 07D - Notas de governanca PowerShell AmazonTech
- Plataforma padrao para administracao auditavel dos endpoints
- Execution Policy: RemoteSigned/AllSigned recomendados; sem Bypass permanente
- Integrar consultas Defender/Firewall/BitLocker em playbooks versionados
- Habilitar logging (Module/ScriptBlock/Transcription) via GPO/Intune quando Pro/Enterprise
- JEA para menor privilegio em tarefas repetitivas
"@ | Set-Content -Path (Join-Path $Docs "Notas_Governanca_PowerShell.txt") -Encoding UTF8

Write-Host "RAW OK"
Write-Host "CAPTURE DONE"
