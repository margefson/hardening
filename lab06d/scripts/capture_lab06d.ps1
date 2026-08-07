# Lab 06D - Governanca e Security Baselines (somente leitura / documentacao)
$ErrorActionPreference = "Continue"
$Base = "d:\MMB\workspace\hardening\lab06d"
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
  "Estacao: WIN-ADM-01 | Lab 06D - Governanca / Security Baselines"
  "Edicao Home: gpedit/secpol tipicamente ausentes - baselines via SCT/LGPO/GPO em Enterprise"
}

Save-Shot "02_sct_baseline" {
  "PS> # Microsoft Security Compliance Toolkit (SCT) - analise documental + busca local"
  $paths = @(
    "$env:ProgramFiles\Microsoft Security Compliance Toolkit*",
    "$env:ProgramFiles(x86)\Microsoft Security Compliance Toolkit*",
    "$env:USERPROFILE\Downloads\*Security*Compliance*",
    "$env:USERPROFILE\Downloads\*LGPO*",
    "C:\Tools\LGPO*",
    "C:\SCT*"
  )
  "Busca por SCT/LGPO no host:"
  foreach ($p in $paths) {
    Get-Item $p -ErrorAction SilentlyContinue | Select-Object FullName
    Get-ChildItem $p -ErrorAction SilentlyContinue | Select-Object -First 5 FullName
  }
  ""
  "Finalidade SCT (referencia Microsoft):"
  "- Disponibilizar Security Baselines oficiais por versao (Win11, Server, Edge, Office, etc.)"
  "- Inclui GPOs pre-configuradas, planilhas de settings, PolicyAnalyzer, LGPO.exe"
  "- Componentes tipicos de baseline: Account Policies, Local Policies/User Rights,"
  "  Security Options, Windows Firewall, Audit Policy, Admin Templates (hardening)"
  ""
  "Baseline alvo AmazonTech (recomendado): Windows 11 / Windows Server (Enterprise)"
  "Beneficio: padronizar WIN-ADM-01 e futuros hosts; reduzir drift administrativo"
  ""
  "PS> Get-HotFix | Select -First 5; (contagem updates)"
  "Hotfixes instalados (amostra): $((Get-HotFix | Measure-Object).Count)"
}

Save-Shot "03_lgpo" {
  "PS> # LGPO.exe - Local Group Policy Object Utility"
  $lgpo = Get-Command LGPO.exe -ErrorAction SilentlyContinue
  "LGPO.exe no PATH: $($null -ne $lgpo)"
  where.exe LGPO.exe 2>&1
  ""
  "Operacoes principais (documentacao SCT):"
  "  LGPO.exe /b <pasta>     # backup politicas locais"
  "  LGPO.exe /g <pasta>     # parse/export GPO"
  "  LGPO.exe /p <arquivo>   # aplicar policy pack"
  "  LGPO.exe /parse /q ...  # converter formato"
  ""
  "Uso AmazonTech: exportar baseline aprovada e replicar em estacoes via script,"
  "sem edicao manual inconsistente de gpedit em cada maquina."
  ""
  "PS> # Estado atual de politicas via registro (amostra UAC / legal notice)"
  $sys = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -ErrorAction SilentlyContinue
  $sys | Select-Object EnableLUA, ConsentPromptBehaviorAdmin, ConsentPromptBehaviorUser, PromptOnSecureDesktop, LegalNoticeCaption, LegalNoticeText |
    Format-List | Out-String
  ""
  "PS> Audit policy (auditpol /get /category:*) - leitura"
  auditpol /get /category:* 2>&1 | Select-Object -First 40
}

Save-Shot "04_gpedit_mmc" {
  "PS> # gpedit.msc / MMC disponibilidade"
  "gpedit.msc: $(Test-Path $env:SystemRoot\System32\gpedit.msc)"
  "secpol.msc: $(Test-Path $env:SystemRoot\System32\secpol.msc)"
  "mmc.exe: $(Test-Path $env:SystemRoot\System32\mmc.exe)"
  "gpmc.msc: $(Test-Path $env:SystemRoot\System32\gpmc.msc)"
  ""
  "Categorias tipicas em gpedit (Computer Configuration):"
  "- Windows Settings > Security Settings (Account/Local/Audit/Firewall)"
  "- Administrative Templates > Windows Components / System / Network"
  "Configuracoes criticas para auditoria: UAC, User Rights, Password Policy,"
  "Audit Logon/Object Access, Windows Defender, Removable Storage, WinRM/SSH"
  ""
  "Snap-ins MMC recomendados para governanca:"
  "1) Group Policy Object Editor / Local Group Policy"
  "2) Security Templates"
  "3) Security Configuration and Analysis"
  "4) Event Viewer"
  "5) Computer Management (Local Users and Groups)"
  ""
  "PS> where.exe mmc"
  where.exe mmc 2>&1
}

Save-Shot "05_sca_compare" {
  "PS> # Security Configuration and Analysis - conceito + comparacao local vs baseline"
  "Finalidade SCA: comparar config atual x template (.inf) e apontar drift."
  ""
  "Comparacao AmazonTech WIN-ADM-01 vs Baseline Microsoft (sintese Labs 06A-C):"
  ""
  "[ADERENTE / PARCIAL]"
  "- UAC EnableLUA=1 (baseline tipica: Enabled)"
  "- Contas Guest/Default desabilitadas (Lab 06A)"
  "- Administrador built-in desabilitado (Lab 06A)"
  "- Inventario identidades/privilegios/NTFS documentado (auditoria)"
  ""
  "[DIVERGENTE / RISCO]"
  "- Conta diaria no grupo Administradores (menor privilegio)"
  "- gpedit/secpol ausentes (edicao Home) - governanca GPO limitada no host"
  "- NTFS Financeiro com Auth Users Modify (Lab 06C) - need-to-know"
  "- Security log ilegivel sem elevacao (Lab 06B)"
  "- SCT/LGPO nao instalados localmente nesta estacao de lab"
  "- Password policy / audit policy nao padronizados via baseline corporativa"
  ""
  "Impacto: drift futuro (updates, novos admins) sem baseline reaplicavel."
}

Save-Shot "06_comparacao_config" {
  "=== COMPARACAO CONFIG ATUAL x BASELINE CORPORATIVA ==="
  "Area                 | Atual (lab)              | Baseline desejada"
  "---------------------|--------------------------|---------------------------"
  "Identidades          | Inventariadas            | Grupos org + contas JIT"
  "Privilegios          | UAC on; admin diario     | Admin separado; URA revisada"
  "NTFS                 | Auth Users amplo         | ACL por GRP_* + heranca doc"
  "Politicas locais     | Parcial (registry/UAC)   | SCT Win11 + LGPO aplicado"
  "Auditoria            | System OK; Security lim. | Auditpol baseline + SIEM"
  "Ferramentas          | MMC parcial              | SCT+LGPO+SCA+Intune/GPO"
  ""
  "Divergencias relevantes? SIM - privilegio permanente + NTFS permissivo +"
  "falta de ferramenta de baseline no host Home."
}

Save-Shot "07_recomendacoes" {
  "=== CONSOLIDACAO RECOMENDACOES GOVERNANCA ==="
  "Padronizacao:"
  "1. Adotar Microsoft Security Compliance Toolkit (Win11/Server) como referencia"
  "2. Aprovar baseline AmazonTech (subset) e versionar em repositorio"
  "3. Aplicar via LGPO (workgroup) ou GPO/Intune (dominio/cloud)"
  ""
  "Monitoramento:"
  "4. SCA / PolicyAnalyzer periodico (mensal)"
  "5. Reauditoria 06A/06B/06C trimestral + apos mudancas"
  "6. Centralizar evidencias e change log"
  ""
  "Revisao periodica:"
  "7. Revisar baseline a cada release Windows / semestral"
  "8. Indicadores: % hosts conformes, tickets drift, HI Lynis (Linux), findings NTFS"
  ""
  "Prioridade alta: (1) baseline+LGPO, (2) remover admin diario, (3) ACL Financeiro"
}

# Plano corporativo de governanca (doc)
$plano = @"
PLANO CORPORATIVO DE GOVERNANCA DA SEGURANCA - AmazonTech (Windows)
Data: $(Get-Date -Format 'dd/MM/yyyy')
Equipe: Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato
Estacao referencia: WIN-ADM-01

1. OBJETIVO DA GOVERNANCA
Garantir que identidades, privilegios, permissoes NTFS e politicas de hardening
permanecam padronizados e aderentes a Security Baselines aprovadas, apesar de
mudancas operacionais, updates e rotatividade de administradores.

2. MECANISMOS DE PADRONIZACAO
- Security Baselines Microsoft (SCT) adaptadas ao perfil AmazonTech
- LGPO.exe para hosts workgroup / golden image
- GPO / Microsoft Intune para dominio e frota gerenciada
- Templates Security Configuration and Analysis
- Documentacao de excecoes com prazo e responsavel

3. FERRAMENTAS RECOMENDADAS
- Microsoft Security Compliance Toolkit (baselines + PolicyAnalyzer)
- LGPO.exe
- MMC (SCA, Event Viewer, Local Users)
- gpedit/secpol (Enterprise/Server) / secedit
- Scripts PowerShell de inventario (Labs 06A-C)
- (Opcional) Microsoft Defender for Endpoint / Intune compliance

4. PERIODICIDADE DAS AUDITORIAS
- Diario: alertas de seguranca / falhas de auth (operacao)
- Semanal: revisao rapida de mudancas privilegiadas
- Mensal: PolicyAnalyzer/SCA vs baseline; amostra NTFS
- Trimestral: ciclo completo identidades + privilegios + NTFS + governanca
- Apos mudanca relevante / upgrade de build: revalidacao baseline

5. RESPONSAVEIS
- Gerencia de Infraestrutura: aplicacao LGPO/GPO e patches
- Seguranca da Informacao: aprovacao baseline e excecoes
- Equipe WIN-ADM: inventario e evidencias
- Diretoria TI: aceite de risco residual

6. INDICADORES
- % estacoes com baseline aplicada (meta >= 95%)
- Numero de contas com admin permanente injustificado (meta = 0)
- Pastas sensiveis com Auth Users/Users indevido (meta = 0)
- Tempo medio para remediacao de drift (meta < 14 dias)
- Evidencias de auditoria arquivadas por ciclo (100%)

7. INTEGRACAO LABS 06A-06D
06A Identidades -> cadastro e grupos
06B Privilegios -> menor privilegio / URA
06C NTFS -> need-to-know / ACL
06D Governanca -> baseline continua + plano permanente
"@
Set-Content (Join-Path $Docs "Plano_Corporativo_Governanca_AmazonTech.txt") -Value $plano -Encoding UTF8

Save-Shot "08_plano_governanca" {
  Get-Content (Join-Path $Docs "Plano_Corporativo_Governanca_AmazonTech.txt") -Raw
}

Get-ChildItem $Shot -Filter "*.txt" | Sort-Object Name | ForEach-Object {
  "===== $($_.Name) ====="
  Get-Content $_.FullName -Raw
  ""
} | Set-Content (Join-Path $Raw "lab06d_full.txt") -Encoding UTF8

Write-Host "CAPTURE DONE"
Get-ChildItem $Shot | Select-Object Name, Length
