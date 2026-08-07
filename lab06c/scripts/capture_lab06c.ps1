# Lab 06C - Auditoria Permissoes NTFS (somente leitura nas ACL existentes)
# Cria arvore de lab para auditoria (nao altera ACL de pastas do sistema)
$ErrorActionPreference = "Continue"
$Base = "d:\MMB\workspace\hardening\lab06c"
$Sim = Join-Path $Base "ambiente_simulado\AmazonTech"
$Shot = Join-Path $Base "evidencias\shots"
$Raw = Join-Path $Base "evidencias\raw"
New-Item -ItemType Directory -Force -Path $Shot, $Raw | Out-Null

# Estrutura corporativa simulada (heranca padrao NTFS)
$dirs = @(
  "$Sim\Financeiro",
  "$Sim\Projetos",
  "$Sim\Auditoria",
  "$Sim\TI",
  "$Sim\Compartilhado"
)
foreach ($d in $dirs) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
"Relatorio financeiro confidencial" | Set-Content "$Sim\Financeiro\relatorio.txt" -Encoding UTF8
"Projeto WEB-01 notes" | Set-Content "$Sim\Projetos\projeto.txt" -Encoding UTF8
"Parecer auditoria identidades" | Set-Content "$Sim\Auditoria\parecer.txt" -Encoding UTF8
"Inventario TI" | Set-Content "$Sim\TI\inventario.txt" -Encoding UTF8
"Arquivo compartilhado geral" | Set-Content "$Sim\Compartilhado\geral.txt" -Encoding UTF8

function Save-Shot($name, [scriptblock]$sb) {
  $path = Join-Path $Shot "$name.txt"
  Set-Content -Path $path -Value ((& $sb 2>&1 | Out-String)) -Encoding UTF8
  Write-Host "OK $name"
}

Save-Shot "01_ambiente" {
  "PS> hostname; whoami; Get-Date"
  hostname; whoami; Get-Date
  $os = Get-CimInstance Win32_OperatingSystem
  "OS: $($os.Caption) | Build: $($os.BuildNumber)"
  "Estacao: WIN-ADM-01 | Lab 06C - Permissoes NTFS"
  "Raiz simulada AmazonTech: $Sim"
}

Save-Shot "02_explorer_security_equiv" {
  "PS> # Equivalente a Propriedades > Seguranca (Explorer)"
  "PS> Pasta auditada: $Sim\Financeiro"
  $acl = Get-Acl "$Sim\Financeiro"
  "Proprietario: $($acl.Owner)"
  "Grupo: $($acl.Group)"
  ""
  "Identidades e permissoes (Access):"
  $acl.Access | Format-Table IdentityReference, FileSystemRights, AccessControlType, IsInherited, InheritanceFlags -AutoSize | Out-String
}

Save-Shot "03_advanced_acl" {
  "PS> # Equivalente a Seguranca > Avancado (ACL/DACL, owner, heranca)"
  foreach ($p in @("$Sim\Financeiro", "$Sim\Projetos", "$Sim\Auditoria", "$Sim")) {
    "===== $p ====="
    $acl = Get-Acl $p
    "Owner: $($acl.Owner)"
    "AreAccessRulesProtected (heranca bloqueada?): $($acl.AreAccessRulesProtected)"
    "AccessRuleCount: $($acl.Access.Count)"
    $acl.Access | Select-Object IdentityReference, FileSystemRights, AccessControlType, IsInherited |
      Format-Table -AutoSize | Out-String
  }
}

Save-Shot "04_effective_access" {
  "PS> # Equivalente Effective Access (calculo via AccessRules + grupos)"
  $target = "$Sim\Financeiro"
  $user = "$env:COMPUTERNAME\marge"
  "Recurso: $target"
  "Identidade: $user"
  ""
  $acl = Get-Acl $target
  "Regras que afetam Usuarios autenticados / Users / marge / Administradores:"
  $acl.Access | Where-Object {
    $_.IdentityReference -match "marge|Users|Usuarios|Administradores|Authenticated|Autenticados|Everyone|Todos"
  } | Format-Table IdentityReference, FileSystemRights, AccessControlType, IsInherited -AutoSize | Out-String
  ""
  "PS> Test-Path / leitura efetiva da sessao atual"
  "Test-Path: $(Test-Path $target)"
  "Get-Content amostra:"
  Get-Content "$target\relatorio.txt"
  ""
  "# Effective Access GUI considera uniao de grupos + Deny wins."
  "# Sessao atual (marge): membro de Usuarios + Administradores (token filtrado)."
  "# Resultado tipico: leitura/escrita herdada de Users/Administrators sobre pasta do laboratorio."
}

Save-Shot "05_icacls" {
  "PS> icacls $Sim"
  icacls $Sim
  ""
  "PS> icacls $Sim\Financeiro"
  icacls "$Sim\Financeiro"
  ""
  "PS> icacls $Sim\Financeiro\relatorio.txt"
  icacls "$Sim\Financeiro\relatorio.txt"
  ""
  "PS> icacls $Sim\Projetos"
  icacls "$Sim\Projetos"
}

Save-Shot "06_get_acl" {
  "PS> Get-Acl $Sim\Financeiro | Format-List"
  Get-Acl "$Sim\Financeiro" | Format-List Path, Owner, Group, AccessToString | Out-String
  ""
  "PS> (Get-Acl ...).Access | Format-List"
  (Get-Acl "$Sim\Financeiro").Access | Format-List IdentityReference, FileSystemRights, AccessControlType, IsInherited, InheritanceFlags, PropagationFlags | Out-String
}

Save-Shot "07_get_childitem" {
  "PS> Get-ChildItem $Sim -Recurse | Select FullName, Mode, Length"
  Get-ChildItem $Sim -Recurse | Select-Object FullName, Mode, Length | Format-Table -AutoSize | Out-String
  ""
  "Total itens: $((Get-ChildItem $Sim -Recurse).Count)"
  "Prioridade auditoria: Financeiro (confidencial), Auditoria, Projetos, TI, Compartilhado"
}

Save-Shot "08_comparacao" {
  "=== COMPARACAO GUI vs CLI ==="
  "Ferramentas: Explorer Seguranca | Avancado | Effective Access | icacls | Get-Acl"
  ""
  "Consistencia observada:"
  "- Owner Financeiro: $((Get-Acl "$Sim\Financeiro").Owner)"
  "- Access count Get-Acl: $((Get-Acl "$Sim\Financeiro").Access.Count)"
  "- icacls lista as mesmas identidades (SID/nomes) com masks (F,M,RX, etc.)"
  "- Heranca: IsInherited=True nas entradas padrao (AreAccessRulesProtected=False)"
  ""
  "Diferencas:"
  "- GUI Effective Access resume resultado final por usuario"
  "- icacls/Get-Acl mostram ACE brutas (melhor para automacao/auditoria em massa)"
  "- Get-Acl AccessToString e legivel; icacls e compacto e scriptavel"
  ""
  "Mais adequada para auditoria corporativa em escala: icacls + Get-Acl (PowerShell)"
  "GUI permanece util para Effective Access e troubleshooting pontual."
}

Save-Shot "09_consolidacao" {
  "=== CONSOLIDACAO LAB 06C - PERMISSOES NTFS ==="
  "Estacao: WIN-ADM-01 / MachadoPC | Usuario: $(whoami)"
  "Ambiente simulado: $Sim"
  ""
  "1) Inventario: $((Get-ChildItem $Sim -Recurse -Directory).Count) pastas + arquivos de amostra"
  "2) ACL Financeiro - identidades:"
  ((Get-Acl "$Sim\Financeiro").Access | ForEach-Object { $_.IdentityReference.Value }) -join "; "
  "3) Heranca ativa (nao protegida): $(-not (Get-Acl "$Sim\Financeiro").AreAccessRulesProtected)"
  "4) Inconsistencias vs politica AmazonTech:"
  "- Pasta Financeiro com heranca ampla (Users/Authenticated) - risco need-to-know"
  "- Sem grupos departamentais (Financeiro/TI) nas ACE - permissoes genericas"
  "- Compartilhado e Financeiro com perfil semelhante - falta segregacao"
  "5) Recomendacoes: grupos por departamento; remover Users de pastas sensiveis;"
  "   documentar heranca; Effective Access nos testes; nao alterar sem change control"
  "6) Proximo: Lab Governanca / Security Baselines"
}

Get-ChildItem $Shot -Filter "*.txt" | Sort-Object Name | ForEach-Object {
  "===== $($_.Name) ====="
  Get-Content $_.FullName -Raw
  ""
} | Set-Content (Join-Path $Raw "lab06c_full.txt") -Encoding UTF8

Write-Host "CAPTURE DONE"
Get-ChildItem $Shot | Select-Object Name, Length
