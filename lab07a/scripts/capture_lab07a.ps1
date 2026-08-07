# Lab 07A - Microsoft Defender (verificacao / leitura; scan rapido se permitido)
$ErrorActionPreference = "Continue"
$Base = "d:\MMB\workspace\hardening\lab07a"
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
  "Estacao: WIN-ADM-01 | Lab 07A - Microsoft Defender"
  "Escopo: validacao da protecao de endpoints (sem alterar configs permanentes)"
}

Save-Shot "02_windows_security" {
  "PS> # Atividade 1 - Plataforma Windows Security / Microsoft Defender"
  $secApp = "$env:ProgramFiles\Windows Defender\MSASCui.exe"
  $secApp2 = "$env:windir\System32\SecurityHealthSystray.exe"
  $secSettings = "$env:windir\System32\windows.immersivecontrolpanel_cw5n1h2txyewy"
  "Windows Defender UI (legado): $(Test-Path $secApp)"
  "SecurityHealthSystray: $(Test-Path $secApp2)"
  "Windows Security (app moderno): via menu Iniciar > Windows Security"
  ""
  "Modulos tipicos da tela inicial (Windows Security):"
  "  - Protecao contra virus e ameacas (Virus & threat protection)"
  "  - Protecao de conta (Account protection)"
  "  - Firewall e protecao de rede"
  "  - Controle de aplicativos e navegador"
  "  - Seguranca do dispositivo"
  "  - Desempenho e saude do dispositivo"
  "  - Opcoes da familia"
  ""
  "PS> Get-Service WinDefend, Sense, MdCoreSvc, SecurityHealthService -ErrorAction SilentlyContinue"
  Get-Service WinDefend, Sense, MdCoreSvc, SecurityHealthService -ErrorAction SilentlyContinue |
    Format-Table Name, Status, StartType -AutoSize | Out-String
  ""
  "PS> Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct"
  Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct -ErrorAction SilentlyContinue |
    Select-Object displayName, pathToSignedProductExe, productState |
    Format-List | Out-String
}

Save-Shot "03_estado_protecao" {
  "PS> # Atividade 2 - Estado da protecao (Get-MpPreference / status)"
  $pref = Get-MpPreference -ErrorAction SilentlyContinue
  $st = Get-MpComputerStatus -ErrorAction SilentlyContinue
  "=== Preferencias (resumo) ==="
  if ($pref) {
    [PSCustomObject]@{
      DisableRealtimeMonitoring     = $pref.DisableRealtimeMonitoring
      MAPSReporting                 = $pref.MAPSReporting
      SubmitSamplesConsent          = $pref.SubmitSamplesConsent
      EnableControlledFolderAccess  = $pref.EnableControlledFolderAccess
      DisableBehaviorMonitoring     = $pref.DisableBehaviorMonitoring
      DisableIOAVProtection         = $pref.DisableIOAVProtection
      DisableScriptScanning         = $pref.DisableScriptScanning
      CloudBlockLevel               = $pref.CloudBlockLevel
      PUAProtection                 = $pref.PUAProtection
    } | Format-List | Out-String
  } else { "Get-MpPreference indisponivel / erro de permissao" }
  ""
  "=== Indicadores de estado ==="
  if ($st) {
    [PSCustomObject]@{
      AntivirusEnabled              = $st.AntivirusEnabled
      AMServiceEnabled              = $st.AMServiceEnabled
      RealTimeProtectionEnabled     = $st.RealTimeProtectionEnabled
      IoavProtectionEnabled         = $st.IoavProtectionEnabled
      NISEnabled                    = $st.NISEnabled
      BehaviorMonitorEnabled        = $st.BehaviorMonitorEnabled
      OnAccessProtectionEnabled     = $st.OnAccessProtectionEnabled
      IsTamperProtected             = $st.IsTamperProtected
      AntivirusSignatureAge         = $st.AntivirusSignatureAge
      QuickScanAge                  = $st.QuickScanAge
    } | Format-List | Out-String
  }
  ""
  "Interpretacao AmazonTech:"
  "- Protecao em tempo real: $($st.RealTimeProtectionEnabled)"
  "- Protecao nuvem (MAPS): MAPSReporting=$($pref.MAPSReporting) (2=Advanced tipico)"
  "- Envio de amostras: SubmitSamplesConsent=$($pref.SubmitSamplesConsent)"
  "- Tamper Protection: IsTamperProtected=$($st.IsTamperProtected)"
}

Save-Shot "04_atualizacoes" {
  "PS> # Atividade 3 - Inteligencia de seguranca / assinaturas"
  $st = Get-MpComputerStatus -ErrorAction SilentlyContinue
  if ($st) {
    [PSCustomObject]@{
      AntivirusSignatureVersion       = $st.AntivirusSignatureVersion
      AntivirusSignatureLastUpdated   = $st.AntivirusSignatureLastUpdated
      AntivirusSignatureAge           = $st.AntivirusSignatureAge
      NISSignatureVersion             = $st.NISSignatureVersion
      NISSignatureLastUpdated         = $st.NISSignatureLastUpdated
      AMEngineVersion                 = $st.AMEngineVersion
      AMProductVersion                = $st.AMProductVersion
      AMServiceVersion                = $st.AMServiceVersion
    } | Format-List | Out-String
  }
  ""
  "PS> Update-MpSignature (somente se permitido; tenta atualizar)"
  try {
    Update-MpSignature -ErrorAction Stop
    "Update-MpSignature: OK"
  } catch {
    "Update-MpSignature: $($_.Exception.Message)"
  }
  $st2 = Get-MpComputerStatus -ErrorAction SilentlyContinue
  "Apos tentativa - AntivirusSignatureVersion: $($st2.AntivirusSignatureVersion)"
  "AntivirusSignatureLastUpdated: $($st2.AntivirusSignatureLastUpdated)"
  "AntivirusSignatureAge (dias): $($st2.AntivirusSignatureAge)"
}

Save-Shot "05_analise_rapida" {
  "PS> # Atividade 4 - Opcoes de verificacao / Analise Rapida"
  "Tipos disponiveis no Microsoft Defender:"
  "  - Analise rapida (QuickScan)"
  "  - Analise completa (FullScan)"
  "  - Analise personalizada (CustomScan)"
  "  - Microsoft Defender Offline"
  ""
  $before = Get-Date
  "PS> Start-MpScan -ScanType QuickScan  (inicio: $before)"
  try {
    Start-MpScan -ScanType QuickScan -ErrorAction Stop
    $after = Get-Date
    $elapsed = ($after - $before).TotalSeconds
    "Resultado: QuickScan concluido sem erro reportado pelo cmdlet"
    "Tempo aproximado: $([math]::Round($elapsed,1)) segundos"
  } catch {
    "QuickScan: $($_.Exception.Message)"
    "Nota: em alguns hosts Home/sem elevacao o scan pode exigir Windows Security GUI"
  }
  ""
  $st = Get-MpComputerStatus -ErrorAction SilentlyContinue
  "QuickScanAge (dias desde ultima rapida): $($st.QuickScanAge)"
  "FullScanAge: $($st.FullScanAge)"
  "ComputerState: $($st.ComputerState)"
}

Save-Shot "06_historico" {
  "PS> # Atividade 5 - Historico de protecao"
  "PS> Get-MpThreatDetection | Select -First 15"
  $det = @(Get-MpThreatDetection -ErrorAction SilentlyContinue | Select-Object -First 15)
  if ($det.Count -eq 0) {
    "Nenhuma deteccao recente retornada por Get-MpThreatDetection."
    "Condicao: historico vazio ou sem ameacas registradas neste endpoint."
  } else {
    $det | Format-Table InitialDetectionTime, ActionSuccess, Resources -AutoSize | Out-String
  }
  ""
  "PS> Get-MpThreat | Select -First 10"
  $th = @(Get-MpThreat -ErrorAction SilentlyContinue | Select-Object -First 10)
  if ($th.Count -eq 0) {
    "Get-MpThreat: sem ameacas ativas/conhecidas na base local."
  } else {
    $th | Format-Table ThreatName, SeverityID, IsActive, DidThreatExecute -AutoSize | Out-String
  }
  ""
  "Observacao: o Historico de Protecao da GUI Windows Security agrega deteccoes,"
  "acoes (quarentena/remover) e eventos administrativos; PowerShell espelha o essencial."
}

Save-Shot "07_mpcomputerstatus" {
  "PS> # Atividade 6 - Consulta administrativa Get-MpComputerStatus"
  "PS> Get-MpComputerStatus"
  Get-MpComputerStatus -ErrorAction SilentlyContinue | Format-List | Out-String
  ""
  "Significado dos indicadores-chave:"
  "  AMServiceEnabled     - servico antimalware (WinDefend) ativo"
  "  AntivirusEnabled     - motor AV habilitado"
  "  RealTimeProtectionEnabled - protecao em tempo real"
  "  AntivirusSignatureVersion - versao da inteligencia de seguranca"
  "  NISEnabled           - Network Inspection System (IDS de rede)"
  "  IsTamperProtected    - protecao contra adulteracao"
}

Save-Shot "08_consolidacao" {
  "PS> # Consolidacao Lab 07A - conformidade AmazonTech"
  $st = Get-MpComputerStatus -ErrorAction SilentlyContinue
  $pref = Get-MpPreference -ErrorAction SilentlyContinue
  "== Checklist protecao basica =="
  "AntivirusEnabled: $($st.AntivirusEnabled)"
  "AMServiceEnabled: $($st.AMServiceEnabled)"
  "RealTimeProtectionEnabled: $($st.RealTimeProtectionEnabled)"
  "IoavProtectionEnabled: $($st.IoavProtectionEnabled)"
  "NISEnabled: $($st.NISEnabled)"
  "BehaviorMonitorEnabled: $($st.BehaviorMonitorEnabled)"
  "IsTamperProtected: $($st.IsTamperProtected)"
  "SignatureAge (dias): $($st.AntivirusSignatureAge)"
  "SignatureVersion: $($st.AntivirusSignatureVersion)"
  "DisableRealtimeMonitoring (pref): $($pref.DisableRealtimeMonitoring)"
  "MAPSReporting: $($pref.MAPSReporting)"
  "SubmitSamplesConsent: $($pref.SubmitSamplesConsent)"
  "PUAProtection: $($pref.PUAProtection)"
  ""
  "Parecer preliminar:"
  if ($st.AntivirusEnabled -and $st.RealTimeProtectionEnabled -and $st.AntivirusSignatureAge -le 7) {
    "ENDPOINT ATENDE necessidades basicas de protecao AmazonTech (camada Defender)."
  } else {
    "ENDPOINT com ressalvas - revisar RTP/assinaturas antes da homologacao."
  }
  "Defender = 1a camada da defesa em profundidade (Firewall, BitLocker, admin, ASR a seguir)."
}

# Raw dump completo
$rawOut = Join-Path $Raw "lab07a_full.txt"
@"
=== Lab 07A raw dump $(Get-Date) ===
$((Get-MpComputerStatus | Format-List | Out-String))
$((Get-MpPreference | Format-List | Out-String))
"@ | Set-Content -Path $rawOut -Encoding UTF8
Write-Host "RAW OK $rawOut"
Write-Host "CAPTURE DONE"
