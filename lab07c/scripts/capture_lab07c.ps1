# Lab 07C - BitLocker (somente verificacao; NAO habilitar criptografia)
$ErrorActionPreference = "Continue"
$Base = "d:\MMB\workspace\hardening\lab07c"
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
  "Estacao: WIN-ADM-01 | Lab 07C - BitLocker"
  "Escopo: verificar disponibilidade/TPM/estado (NAO habilitar BitLocker)"
}

Save-Shot "02_disponibilidade_bitlocker" {
  "PS> # Atividade 1 - Disponibilidade do BitLocker"
  $os = Get-CimInstance Win32_OperatingSystem
  "Edicao Windows: $($os.Caption)"
  "ProductType: $($os.ProductType) | OSArchitecture: $($os.OSArchitecture)"
  ""
  "Caminhos / features relacionadas:"
  "BitLocker Control Panel CPL: $(Test-Path $env:SystemRoot\System32\BitLockerCpl.dll)"
  "manage-bde.exe: $(Test-Path $env:SystemRoot\System32\manage-bde.exe)"
  "BitLocker Wizard: $(Test-Path $env:SystemRoot\System32\BitLockerWizard.exe)"
  "fveapi.dll: $(Test-Path $env:SystemRoot\System32\fveapi.dll)"
  ""
  "PS> Get-WindowsOptionalFeature -Online -FeatureName BitLocker* (pode exigir admin)"
  try {
    Get-WindowsOptionalFeature -Online -FeatureName *BitLocker* -ErrorAction Stop |
      Select-Object FeatureName, State |
      Format-Table -AutoSize | Out-String
  } catch {
    "Get-WindowsOptionalFeature: $($_.Exception.Message)"
  }
  ""
  "PS> Get-Service -Name BDESVC -ErrorAction SilentlyContinue"
  Get-Service -Name BDESVC -ErrorAction SilentlyContinue |
    Format-Table Name, Status, StartType -AutoSize | Out-String
  ""
  "Device Encryption (Home) - registro DeviceEncryption:"
  $de = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\BitLocker" -ErrorAction SilentlyContinue
  if ($de) { $de | Format-List | Out-String } else { "HKLM\...\BitLocker: chave ausente ou sem acesso" }
  ""
  "Nota Home: BitLocker Drive Encryption completo tipicamente Pro/Enterprise;"
  "Device Encryption pode existir em hardware elegivel (Modern Standby/TPM)."
}

Save-Shot "03_tpm" {
  "PS> # Atividade 2 - Trusted Platform Module (TPM)"
  "tpm.msc presente: $(Test-Path $env:SystemRoot\System32\tpm.msc)"
  ""
  "PS> Get-Tpm"
  try {
    Get-Tpm | Format-List | Out-String
  } catch {
    "Get-Tpm: $($_.Exception.Message)"
  }
  ""
  "PS> Get-CimInstance -Namespace root/cimv2/Security/MicrosoftTpm -ClassName Win32_Tpm"
  try {
    Get-CimInstance -Namespace "root/cimv2/Security/MicrosoftTpm" -ClassName Win32_Tpm -ErrorAction Stop |
      Select-Object IsActivated_InitialValue, IsEnabled_InitialValue, IsOwned_InitialValue, SpecVersion, ManufacturerVersion, ManufacturerIdTxt |
      Format-List | Out-String
  } catch {
    "Win32_Tpm: $($_.Exception.Message)"
  }
  ""
  "Importancia TPM: armazenar chaves de selagem (PCR), atestar integridade do boot"
  "e permitir desbloqueio automatico do BitLocker sem digitar senha a cada boot"
  "(quando politica corporativa permite TPM-only ou TPM+PIN)."
}

Save-Shot "04_manage_bde_status" {
  "PS> # Atividade 3 - Estado das unidades (manage-bde -status)"
  "PS> manage-bde -status"
  manage-bde -status 2>&1 | Out-String
  ""
  "PS> Get-Volume | Select DriveLetter, FileSystemLabel, FileSystem, Size, SizeRemaining"
  Get-Volume -ErrorAction SilentlyContinue |
    Where-Object { $_.DriveLetter } |
    Select-Object DriveLetter, FileSystemLabel, FileSystem, @{N='SizeGB';E={[math]::Round($_.Size/1GB,1)}}, HealthStatus |
    Format-Table -AutoSize | Out-String
}

Save-Shot "05_powershell_bitlocker" {
  "PS> # Atividade 4 - Cmdlets administrativos BitLocker"
  "PS> Get-Command *BitLocker*"
  Get-Command *BitLocker* -ErrorAction SilentlyContinue |
    Select-Object Name, CommandType, Source |
    Format-Table -AutoSize | Out-String
  ""
  "PS> Get-BitLockerVolume"
  try {
    Get-BitLockerVolume -ErrorAction Stop | Format-List | Out-String
  } catch {
    "Get-BitLockerVolume: $($_.Exception.Message)"
    "Interpretacao: cmdlet pode exigir modulo BitLocker + edicao Pro/Enterprise + elevacao."
  }
  ""
  "PS> Get-Module -ListAvailable BitLocker"
  Get-Module -ListAvailable BitLocker -ErrorAction SilentlyContinue |
    Format-Table Name, Version, Path -AutoSize | Out-String
}

Save-Shot "06_recuperacao" {
  "PS> # Atividade 5 - Opcoes de recuperacao (exploracao; SEM alterar)"
  "Interface tipica (Pro): Painel de Controle > BitLocker > Fazer backup da chave de recuperacao"
  "Opcoes comuns de backup:"
  "  - Conta Microsoft"
  "  - Conta / pasta de trabalho (AD/Azure AD - corporativo)"
  "  - Arquivo USB / impressao (48 digitos)"
  ""
  "Finalidade da chave de recuperacao:"
  "  Permitir desbloqueio da unidade quando TPM falha, hardware muda,"
  "  PIN esquecido, ou boot em ambiente nao confiavel (recovery mode)."
  "  Sem a chave, dados criptografados ficam inacessiveis - custodia corporativa obrigatoria."
  ""
  "PS> manage-bde -protectors -get C:  (somente leitura; pode falhar sem BitLocker/admin)"
  manage-bde -protectors -get C: 2>&1 | Out-String
  ""
  "PS> # Protectors em outras letras (se existirem)"
  Get-Volume -ErrorAction SilentlyContinue | Where-Object { $_.DriveLetter } | ForEach-Object {
    $d = "$($_.DriveLetter):"
    "--- protectors $d ---"
    manage-bde -protectors -get $d 2>&1 | Select-Object -First 12
  }
  ""
  "NENHUMA chave foi gerada/alterada/apagada nesta atividade (restricao OS)."
}

Save-Shot "07_aptidao_hardware" {
  "PS> # Aptidao para politica AmazonTech (notebooks externos)"
  $os = Get-CimInstance Win32_OperatingSystem
  $tpm = $null
  try { $tpm = Get-Tpm } catch {}
  $cs = Get-CimInstance Win32_ComputerSystem
  "Edicao: $($os.Caption)"
  "Chassis/Model: $($cs.Manufacturer) $($cs.Model)"
  "PCSystemType: $($cs.PCSystemType) (2=Mobile/Notebook tipico)"
  if ($tpm) {
    "TPM Present=$($tpm.TpmPresent) Ready=$($tpm.TpmReady) Enabled=$($tpm.TpmEnabled) Activated=$($tpm.TpmActivated)"
  } else { "TPM: nao consultavel" }
  "manage-bde disponivel: $(Test-Path $env:SystemRoot\System32\manage-bde.exe)"
  "BDESVC: $((Get-Service BDESVC -EA SilentlyContinue).Status)"
  ""
  "Criterios AmazonTech (criptografia obrigatoria em notebooks externos):"
  "  1) Edicao com BitLocker completo (Pro/Enterprise/Education) OU Device Encryption"
  "  2) TPM 2.0 preferencialmente Ready"
  "  3) Custodia de recovery key no AD/Entra ID / cofre corporativo"
  "  4) Politica: TPM+PIN para alto risco; suspender so em manutencao autorizada"
}

Save-Shot "08_consolidacao" {
  "PS> # Consolidacao Lab 07C - parecer"
  $os = (Get-CimInstance Win32_OperatingSystem).Caption
  $isHome = $os -match 'Home'
  $tpmOk = $false
  try { $tpmOk = (Get-Tpm).TpmPresent } catch {}
  "Windows: $os"
  "BitLocker UI/feature completa tipica de Pro: $(-not $isHome) (isHome=$isHome)"
  "TPM presente: $tpmOk"
  "Status unidades: ver evidencia manage-bde (04)"
  ""
  "Parecer preliminar:"
  if ($isHome) {
    "EDICAO HOME: BitLocker Drive Encryption completo geralmente AUSENTE;"
    "equipamento requer upgrade para Pro/Enterprise OU Device Encryption elegivel"
    "antes da politica obrigatoria AmazonTech em notebooks externos."
  } else {
    "Edicao apta a BitLocker completo; validar Encryption Percentage / Protection Status."
  }
  "Papel BitLocker: confidencialidade em repouso (perda/roubo do disco/notebook)."
  "Nenhuma criptografia foi ativada nesta OS (somente auditoria)."
}

@"
=== Lab 07C raw dump $(Get-Date) ===
OS: $((Get-CimInstance Win32_OperatingSystem).Caption)
$((try { Get-Tpm | Format-List | Out-String } catch { $_.Exception.Message }))
$((manage-bde -status 2>&1 | Out-String))
"@ | Set-Content -Path (Join-Path $Raw "lab07c_full.txt") -Encoding UTF8
Write-Host "RAW OK"
Write-Host "CAPTURE DONE"
