# Lab 07B - Windows Defender Firewall (somente consulta / verificacao)
$ErrorActionPreference = "Continue"
$Base = "d:\MMB\workspace\hardening\lab07b"
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
  "Estacao: WIN-ADM-01 | Lab 07B - Windows Defender Firewall"
  "Escopo: validacao das politicas de comunicacao (sem alterar regras)"
}

Save-Shot "02_perfis_firewall" {
  "PS> # Atividade 1 - Perfis Domain / Private / Public"
  "PS> Get-NetFirewallProfile | Format-Table Name, Enabled, DefaultInboundAction, DefaultOutboundAction, LogAllowed, LogBlocked -AutoSize"
  Get-NetFirewallProfile | Format-Table Name, Enabled, DefaultInboundAction, DefaultOutboundAction, LogFileName, LogMaxSizeKilobytes, LogAllowed, LogBlocked -AutoSize | Out-String
  ""
  "PS> Get-NetConnectionProfile (perfil de rede ativo)"
  Get-NetConnectionProfile -ErrorAction SilentlyContinue |
    Select-Object Name, InterfaceAlias, NetworkCategory, IPv4Connectivity |
    Format-List | Out-String
  ""
  "Servico MpsSvc (Windows Defender Firewall):"
  Get-Service MpsSvc -ErrorAction SilentlyContinue | Format-Table Name, Status, StartType -AutoSize | Out-String
  "wf.msc presente: $(Test-Path $env:SystemRoot\System32\wf.msc)"
}

Save-Shot "03_console_avancado" {
  "PS> # Atividade 2 - Console avancado (wf.msc) - inventario via PowerShell"
  "Console: Windows Defender Firewall with Advanced Security (wf.msc)"
  "Nos tipicos: Regras de Entrada | Regras de Saida | Seguranca de Conexao | Monitoramento"
  ""
  $all = @(Get-NetFirewallRule -ErrorAction SilentlyContinue)
  $in = @($all | Where-Object { $_.Direction -eq 'Inbound' })
  $out = @($all | Where-Object { $_.Direction -eq 'Outbound' })
  $enIn = @($in | Where-Object { $_.Enabled -eq 'True' })
  $enOut = @($out | Where-Object { $_.Enabled -eq 'True' })
  "Total de regras: $($all.Count)"
  "Entrada (Inbound): $($in.Count) | habilitadas: $($enIn.Count)"
  "Saida (Outbound): $($out.Count) | habilitadas: $($enOut.Count)"
  ""
  "PS> Get-NetIPsecRule (regras de seguranca de conexao / IPsec)"
  $ipsec = @(Get-NetIPsecRule -ErrorAction SilentlyContinue)
  "Quantidade IPsec/Connection Security: $($ipsec.Count)"
  if ($ipsec.Count -gt 0) {
    $ipsec | Select-Object -First 5 DisplayName, Enabled, Mode | Format-Table -AutoSize | Out-String
  } else {
    "Nenhuma regra IPsec ativa listada (comum em estacao workgroup)."
  }
  ""
  "Monitoramento (ativo): regras habilitadas + filtro por perfil corrente"
  $active = Get-NetConnectionProfile -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty NetworkCategory
  "Categoria de rede atual: $active"
}

Save-Shot "04_regras_amostra" {
  "PS> # Atividade 3 - Identificando regras (amostra detalhada)"
  "Selecao de duas regras representativas + propriedades"
  ""
  $candidates = @(
    Get-NetFirewallRule -DisplayName '*Remote Desktop*' -ErrorAction SilentlyContinue | Select-Object -First 1
    Get-NetFirewallRule -DisplayName '*File and Printer Sharing*' -ErrorAction SilentlyContinue | Select-Object -First 1
    Get-NetFirewallRule -DisplayName '*Core Networking*' -ErrorAction SilentlyContinue | Select-Object -First 1
    Get-NetFirewallRule -Enabled True -Direction Inbound -ErrorAction SilentlyContinue | Select-Object -First 1
  ) | Where-Object { $_ } | Select-Object -First 2

  if ($candidates.Count -lt 2) {
    $candidates = @(Get-NetFirewallRule -Enabled True -ErrorAction SilentlyContinue | Select-Object -First 2)
  }

  $i = 1
  foreach ($r in $candidates) {
    "=== Regra $i : $($r.DisplayName) ==="
    $port = Get-NetFirewallPortFilter -AssociatedNetFirewallRule $r -ErrorAction SilentlyContinue
    $app = Get-NetFirewallApplicationFilter -AssociatedNetFirewallRule $r -ErrorAction SilentlyContinue
    $addr = Get-NetFirewallAddressFilter -AssociatedNetFirewallRule $r -ErrorAction SilentlyContinue
    [PSCustomObject]@{
      Nome       = $r.DisplayName
      Direcao    = $r.Direction
      Acao       = $r.Action
      Enabled    = $r.Enabled
      Perfil     = $r.Profile
      Programa   = $app.Program
      Protocolo  = $port.Protocol
      PortaLocal = $port.LocalPort
      Remoto     = $addr.RemoteAddress
    } | Format-List | Out-String
    $i++
  }
}

Save-Shot "05_powershell_admin" {
  "PS> # Atividade 4 - Consulta administrativa PowerShell"
  "PS> Get-NetFirewallProfile"
  Get-NetFirewallProfile | Format-List Name, Enabled, DefaultInboundAction, DefaultOutboundAction, NotifyOnListen, AllowInboundRules, AllowLocalFirewallRules | Out-String
  ""
  "PS> Get-NetFirewallRule | Select-Object -First 10"
  Get-NetFirewallRule -ErrorAction SilentlyContinue |
    Select-Object -First 10 DisplayName, Direction, Action, Enabled, Profile |
    Format-Table -AutoSize | Out-String
  ""
  "Finalidade: inventariar estado dos perfis e amostrar regras sem abrir GUI;"
  "base para auditoria, baseline e deteccao de excecoes temporarias esquecidas."
  $total = (Get-NetFirewallRule -ErrorAction SilentlyContinue | Measure-Object).Count
  "Volume total de regras retornaveis: $total"
}

Save-Shot "06_exportacao" {
  "PS> # Atividade 5 - Exportacao da politica (exploracao; sem alterar)"
  "Localizacao tipica (wf.msc):"
  "  Painel direito / Acao > Export Policy... (Exportar Politica)"
  "  Ou: netsh advfirewall export <arquivo.wfw>"
  ""
  "Finalidade da exportacao:"
  "  - Backup da configuracao atual antes de mudancas"
  "  - Replicacao/padronizacao entre endpoints (golden image / baseline)"
  "  - Evidencia forense e comparacao de drift entre departamentos"
  "  - Importacao controlada em janela de mudanca autorizada"
  ""
  "PS> # Demonstracao segura: listar sintaxe (NAO exporta para producao critica)"
  "Comando de referencia (nao executado para gravar em path de sistema):"
  "  netsh advfirewall export `"$env:TEMP\AmazonTech_FW_Lab07B.wfw`""
  ""
  $exportPath = Join-Path $Docs "AmazonTech_FW_Lab07B_export.wfw"
  "PS> netsh advfirewall export (copia de evidencia em evidencias\docs)"
  $result = netsh advfirewall export $exportPath 2>&1
  $result | Out-String
  "Arquivo gerado: $(Test-Path $exportPath) -> $exportPath"
  if (Test-Path $exportPath) {
    $fi = Get-Item $exportPath
    "Tamanho: $($fi.Length) bytes | Data: $($fi.LastWriteTime)"
  }
  "Nota OS: exportacao e leitura/backup; nenhuma regra foi criada/alterada/removida."
}

Save-Shot "07_regras_habilitadas" {
  "PS> # Complemento - regras habilitadas por direcao (amostra auditoria)"
  "Inbound Enabled (Top 15 por DisplayName):"
  Get-NetFirewallRule -Enabled True -Direction Inbound -ErrorAction SilentlyContinue |
    Select-Object -First 15 DisplayName, Action, Profile |
    Format-Table -AutoSize | Out-String
  ""
  "Outbound Enabled (Top 10):"
  Get-NetFirewallRule -Enabled True -Direction Outbound -ErrorAction SilentlyContinue |
    Select-Object -First 10 DisplayName, Action, Profile |
    Format-Table -AutoSize | Out-String
  ""
  "Default actions (resumo):"
  Get-NetFirewallProfile | ForEach-Object {
    "$($_.Name): In=$($_.DefaultInboundAction) Out=$($_.DefaultOutboundAction) Enabled=$($_.Enabled)"
  }
}

Save-Shot "08_consolidacao" {
  "PS> # Consolidacao Lab 07B - conformidade AmazonTech"
  $profiles = Get-NetFirewallProfile
  foreach ($p in $profiles) {
    "Perfil $($p.Name): Enabled=$($p.Enabled) InDefault=$($p.DefaultInboundAction) OutDefault=$($p.DefaultOutboundAction)"
  }
  $cat = (Get-NetConnectionProfile | Select-Object -First 1).NetworkCategory
  "Rede ativa (NetworkCategory): $cat"
  $total = (Get-NetFirewallRule | Measure-Object).Count
  $en = (Get-NetFirewallRule -Enabled True | Measure-Object).Count
  "Regras totais=$total | habilitadas=$en"
  "MpsSvc: $((Get-Service MpsSvc).Status)"
  "Export .wfw: $(Test-Path (Join-Path $Docs 'AmazonTech_FW_Lab07B_export.wfw'))"
  ""
  "Parecer preliminar:"
  $allOn = @($profiles | Where-Object { $_.Enabled -eq $true }).Count -eq 3
  if ($allOn) {
    "FIREWALL ATENDE necessidades basicas: 3 perfis habilitados; padrao inbound Block tipico."
  } else {
    "FIREWALL com ressalvas - algum perfil desabilitado; revisar antes da homologacao."
  }
  "Proximo passo corporativo: revisar excecoes temporarias; baseline GPO/Intune; logging."
}

# Raw dump
@"
=== Lab 07B raw dump $(Get-Date) ===
$((Get-NetFirewallProfile | Format-List | Out-String))
$((Get-NetConnectionProfile | Format-List | Out-String))
TotalRules=$((Get-NetFirewallRule | Measure-Object).Count)
"@ | Set-Content -Path (Join-Path $Raw "lab07b_full.txt") -Encoding UTF8
Write-Host "RAW OK"
Write-Host "CAPTURE DONE"
