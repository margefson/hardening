# Lab 07E - Avaliacao de Hardening de Servicos (SOMENTE LEITURA; nao desabilitar nada)
$ErrorActionPreference = "Continue"
$Base = "d:\MMB\workspace\hardening\lab07e"
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
  "Estacao: WIN-ADM-01 | Lab 07E - Hardening de Servicos"
  "Escopo: avaliacao da superficie de ataque (NAO desabilitar servicos)"
}

Save-Shot "02_servicos" {
  "PS> # Atividade 1 - Servicos Windows (equiv. services.msc)"
  "services.msc presente: $(Test-Path $env:SystemRoot\System32\services.msc)"
  $all = @(Get-Service)
  $run = @($all | Where-Object Status -eq 'Running')
  $stop = @($all | Where-Object Status -eq 'Stopped')
  "Total: $($all.Count) | Running: $($run.Count) | Stopped: $($stop.Count)"
  ""
  "Distribuicao por StartType:"
  $all | Group-Object StartType | Sort-Object Count -Descending |
    Select-Object Name, Count | Format-Table -AutoSize | Out-String
  ""
  "=== Tres servicos selecionados (amostra analitica) ==="
  $pick = @(
    Get-Service WinDefend -ErrorAction SilentlyContinue
    Get-Service Spooler -ErrorAction SilentlyContinue
    Get-Service RemoteRegistry -ErrorAction SilentlyContinue
  )
  foreach ($s in $pick) {
    if (-not $s) { continue }
    $cim = Get-CimInstance Win32_Service -Filter "Name='$($s.Name)'" -ErrorAction SilentlyContinue
    "--- $($s.Name) ---"
    "DisplayName : $($s.DisplayName)"
    "Status      : $($s.Status)"
    "StartType   : $($s.StartType)"
    "StartMode   : $($cim.StartMode)"
    "PathName    : $($cim.PathName)"
    switch ($s.Name) {
      'WinDefend' { "Finalidade: motor Microsoft Defender Antivirus (manter Running)." }
      'Spooler' { "Finalidade: fila de impressao; candidata a revisao se endpoint sem impressora." }
      'RemoteRegistry' { "Finalidade: registro remoto; tipicamente desnecessario - superficie." }
    }
    ""
  }
  ""
  "Amostra Running (15):"
  $run | Select-Object -First 15 Name, Status, StartType | Format-Table -AutoSize | Out-String
}

Save-Shot "03_startup" {
  "PS> # Atividade 2 - Programas de inicializacao automatica"
  "PS> Get-CimInstance Win32_StartupCommand"
  Get-CimInstance Win32_StartupCommand -ErrorAction SilentlyContinue |
    Select-Object Name, Command, Location, User |
    Format-Table -Wrap -AutoSize | Out-String
  ""
  "PS> Startup Approved (HKCU/HKLM Run)"
  "HKCU\\...\\Run:"
  Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue |
    Select-Object * -ExcludeProperty PS* | Format-List | Out-String
  "HKLM\\...\\Run:"
  Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue |
    Select-Object * -ExcludeProperty PS* | Format-List | Out-String
  ""
  "PS> Get-StartupApp (se disponivel) / Task Manager Startup equiv."
  try {
    Get-CimInstance MSFT_ScheduledTask -Namespace root/Microsoft/Windows/TaskScheduler -ErrorAction Stop |
      Where-Object { $_.TaskPath -notmatch '\\Microsoft\\' -and $_.State -eq 4 } |
      Select-Object -First 5 TaskName, TaskPath, State |
      Format-Table -AutoSize | Out-String
  } catch {
    "ScheduledTask CIM: $($_.Exception.Message)"
  }
  ""
  "msconfig presente: $(Test-Path $env:SystemRoot\System32\msconfig.exe)"
  "Observacao: impacto (Alto/Medio/Baixo) tipicamente visto no Gerenciador de Tarefas > Inicializar."
}

Save-Shot "04_recursos_opcionais" {
  "PS> # Atividade 3 - Recursos opcionais do Windows"
  "PS> Get-WindowsOptionalFeature -Online (pode exigir elevacao)"
  try {
    $feat = Get-WindowsOptionalFeature -Online -ErrorAction Stop
    "Total features: $($feat.Count)"
    "Enabled: $((@($feat | Where-Object State -eq 'Enabled')).Count)"
    "Disabled: $((@($feat | Where-Object State -eq 'Disabled')).Count)"
    ""
    "Exemplos Enabled (amostra):"
    $feat | Where-Object State -eq 'Enabled' |
      Select-Object -First 20 FeatureName, State |
      Format-Table -AutoSize | Out-String
    ""
    "Candidatos tipicos a revisao AmazonTech (se Enabled):"
    $watch = 'TelnetClient','TFTP','SMB1Protocol','SimpleTCP','IIS-WebServerRole','Microsoft-Windows-Subsystem-Linux','Containers','HypervisorPlatform','Windows-Defender-ApplicationGuard'
    $feat | Where-Object { $watch -contains $_.FeatureName } |
      Select-Object FeatureName, State | Format-Table -AutoSize | Out-String
  } catch {
    "Get-WindowsOptionalFeature: $($_.Exception.Message)"
    ""
    "PS> Fallback - DISM / Get-WindowsCapability (amostra)"
    try {
      Get-WindowsCapability -Online -ErrorAction Stop |
        Where-Object State -eq 'Installed' |
        Select-Object -First 15 Name, State |
        Format-Table -AutoSize | Out-String
    } catch {
      "Get-WindowsCapability: $($_.Exception.Message)"
    }
    "Interface GUI: Configuracoes > Aplicativos > Recursos opcionais"
    "ou Painel de Controle > Programas > Ativar ou desativar recursos do Windows"
  }
}

Save-Shot "05_powershell_admin" {
  "PS> # Atividade 4 - Consulta administrativa PowerShell"
  "PS> Get-Service | Group-Object Status | Select Name, Count"
  Get-Service | Group-Object Status | Select-Object Name, Count | Format-Table -AutoSize | Out-String
  ""
  "PS> Get-Service | Where-Object StartType -eq 'Automatic' | Measure"
  "Automatic: $((@(Get-Service | Where-Object StartType -eq 'Automatic')).Count)"
  "AutomaticDelayedStart: $((@(Get-Service | Where-Object StartType -eq 'AutomaticDelayedStart')).Count)"
  "Manual: $((@(Get-Service | Where-Object StartType -eq 'Manual')).Count)"
  "Disabled: $((@(Get-Service | Where-Object StartType -eq 'Disabled')).Count)"
  ""
  "Comparacao GUI vs PowerShell:"
  "- services.msc = mesma base SCM; PS permite filtro/export/auditoria em massa"
  "- Recursos opcionais: GUI 'Ativar/desativar' ~= Get-WindowsOptionalFeature -Online"
  "- Startup: Task Manager ~= Win32_StartupCommand + Run keys"
}

Save-Shot "06_superficie_ataque" {
  "PS> # Complemento - indicadores de superficie de ataque"
  "Servicos Automatic + Running (amostra nao-Microsoft suspeita / revisao):"
  Get-CimInstance Win32_Service -ErrorAction SilentlyContinue |
    Where-Object { $_.StartMode -eq 'Auto' -and $_.State -eq 'Running' -and $_.PathName -notmatch 'Windows|System32|SysWOW64' } |
    Select-Object -First 15 Name, DisplayName, StartMode, State |
    Format-Table -Wrap -AutoSize | Out-String
  ""
  "Servicos historicamente sensiveis (estado atual):"
  $sens = 'RemoteRegistry','Telnet','TlntSvr','SSDPSRV','upnphost','RemoteAccess','SharedAccess','TermService','WinRM','Fax','XblGameSave','XboxGipSvc','XboxNetApiSvc','WMPNetworkSvc','RemoteAccess'
  foreach ($n in ($sens | Select-Object -Unique)) {
    $s = Get-Service -Name $n -ErrorAction SilentlyContinue
    if ($s) { "{0,-18} Status={1,-10} Start={2}" -f $s.Name, $s.Status, $s.StartType }
  }
  ""
  "Aplicativos instalados (amostra Get-Package / Appx - contagem):"
  "Win32 packages (Get-Package): $((@(Get-Package -ErrorAction SilentlyContinue)).Count)"
  "Appx provisioned (usuario): $((@(Get-AppxPackage -ErrorAction SilentlyContinue)).Count)"
}

Save-Shot "07_plano_hardening" {
  "PS> # Atividade 5 - Plano preliminar de Hardening (SEM alterar)"
  "Tabela: Item | Situacao observada | Recomendacao"
  ""
  "1. RemoteRegistry | Verificar StartType/Status | Manter Disabled se nao houver necessidade remota"
  "2. Spooler | Running/Automatic tipico | Desabilitar em hosts sem impressao (apos aceite)"
  "3. Xbox* / WMPNetworkSvc | Se presentes | Desabilitar em endpoints corporativos"
  "4. Startup (HKCU/HKLM Run) | Itens de terceiros | Revisar impacto; remover nao essenciais"
  "5. SMB1 / Telnet / TFTP | Se Enabled | Remover feature (superficie legado)"
  "6. IIS / Containers / WSL | Se Enabled sem demanda | Desinstalar ou restringir"
  "7. Servicos Automatic nao-Microsoft | Paths fora System32 | Inventariar; justificar ou remover"
  "8. WinDefend / MpsSvc | Running | MANTER (nucleo Labs 07A/07B)"
  ""
  "Justificativa geral: menor funcionalidade + menor superficie; mudancas so em janela autorizada."
  "Documento completo: evidencias/docs/Plano_Preliminar_Hardening_Servicos.txt"
}

Save-Shot "08_consolidacao" {
  "PS> # Consolidacao Lab 07E - parecer AmazonTech"
  $all = @(Get-Service)
  "Servicos: total=$($all.Count) running=$((@($all|? Status -eq Running)).Count) stopped=$((@($all|? Status -eq Stopped)).Count)"
  "Startup entries (Win32_StartupCommand): $((@(Get-CimInstance Win32_StartupCommand -EA SilentlyContinue)).Count)"
  "Nenhum servico foi parado/desabilitado nesta OS."
  ""
  "Parecer preliminar:"
  "Avaliacao de Hardening CONCLUIDA - endpoint com oportunidades de reducao de superficie"
  "(servicos/startup/features), sem comprometimento dos controles 07A-07D."
  "Proximo passo: priorizar plano preliminar sob change control + baseline GPO/Intune."
  "Ciclo Aula 7 (07A-07E) completo em nivel de auditoria/planejamento."
}

# Plano documental
@"
PLANO PRELIMINAR DE HARDENING DE SERVICOS - AmazonTech / WIN-ADM-01
Data: $(Get-Date -Format 'dd/MM/yyyy')
Equipe: Josias Bentes, Keven Coimbra, Margefson Barros, Nattan Lobato
Restricao: NENHUMA alteracao aplicada neste laboratorio (apenas avaliacao).

Item Avaliado                 | Situacao Observada                         | Recomendacao                         | Justificativa
------------------------------|--------------------------------------------|--------------------------------------|---------------------------
RemoteRegistry                | Inventariado (superficie remota)           | Manter/Disabled se sem uso           | Reduz registro remoto
Spooler                       | Tipicamente Automatic/Running              | Revisar; desabilitar se sem impressao| Menor funcionalidade
Xbox*/WMPNetworkSvc           | Servicos de consumo                        | Desabilitar em endpoints corporativos| Sem demanda de negocio
Programas Startup (Run keys)  | Entradas HKCU/HKLM + StartupCommand        | Remover nao essenciais               | Acelera boot; reduz malware persistente
SMB1/Telnet/TFTP              | Verificar Optional Features                | Remover se Enabled                   | Protocolos legados inseguros
IIS/WSL/Containers            | Verificar se Enabled sem projeto           | Desinstalar ou restringir            | Superficie de ataque extra
Servicos Auto fora System32   | Paths de terceiros                         | Inventariar e justificar              | Software nao padronizado
WinDefend + MpsSvc            | Controles Labs 07A/07B                     | MANTER ativos                        | Nucleo de protecao endpoint
Execution Policy / Logging PS | Lab 07D                                    | Baseline RemoteSigned + logging       | Governanca administrativa
BitLocker/Device Encryption   | Lab 07C (Home parcial)                     | Upgrade Pro + recovery key            | Dados em repouso

Prioridade sugerida: (1) RemoteRegistry/legado (2) Startup (3) Features opcionais (4) Spooler/Xbox (5) BitLocker edicao.
"@ | Set-Content -Path (Join-Path $Docs "Plano_Preliminar_Hardening_Servicos.txt") -Encoding UTF8

@"
=== Lab 07E raw $(Get-Date) ===
$((Get-Service | Group-Object Status | Format-Table | Out-String))
StartupCount=$((@(Get-CimInstance Win32_StartupCommand -EA SilentlyContinue)).Count)
"@ | Set-Content -Path (Join-Path $Raw "lab07e_full.txt") -Encoding UTF8

Write-Host "RAW OK"
Write-Host "CAPTURE DONE"
