<p align="center">
  <img src="assets/logo.png" alt="Hardening logo" width="160" height="160" />
</p>

<h1 align="center">Hardening — Windows e Linux</h1>

<p align="center">
  Repositório público de entregas práticas da disciplina <b>Windows e Linux Hardening</b>,<br/>
  com foco em diagnóstico, endurecimento e auditoria de um servidor Linux corporativo simulado<br/>
  (<b>AmazonTech / WEB-01</b>).
</p>

<p align="center">
  <b>Equipe:</b> Josias Bentes · Keven Coimbra · Margefson Barros · Nattan Lobato
</p>

---

---

## Objetivo do projeto

Construir, ao longo das aulas, uma linha de base de segurança para um servidor Linux, documentando cada etapa com:

- inventário técnico e evidências de terminal;
- correções alinhadas ao princípio do **menor privilégio** e da **menor funcionalidade**;
- PDFs de entrega (Ordem de Serviço + relatório técnico);
- pareceres fundamentados apenas em evidências coletadas.

O ambiente de laboratório utilizado foi **Debian GNU/Linux 13 (trixie)** em WSL (`hostname: MachadoPC`), representando o servidor **WEB-01**.

---

## Estrutura do repositório

```text
hardening/
├── lab01/                 # Inventário Inicial de Segurança
│   ├── entregaveis/       # PDFs para entrega
│   ├── evidencias/        # Saídas de terminal e screenshots
│   └── scripts/           # Coleta e geração de PDFs
├── lab02/                 # Identidades e Privilégios
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab03/                 # Redução da Superfície de Ataque
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab04a/                # Mandatory Access Control (SELinux/AppArmor)
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab04b/                # Manutenção Contínua do Hardening
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab06a/                # Auditoria das Identidades Windows
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab06b/                # Auditoria dos Privilégios Administrativos
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab06c/                # Auditoria das Permissões NTFS
│   ├── entregaveis/
│   ├── evidencias/
│   ├── ambiente_simulado/ # Árvore AmazonTech para auditoria
│   └── scripts/
├── lab06d/                # Governança e Security Baselines
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab07a/                # Microsoft Defender (endpoints)
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab07b/                # Windows Defender Firewall
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab07c/                # BitLocker (criptografia de unidades)
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab07d/                # Administração Segura com PowerShell
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
├── lab07e/                # Hardening de Serviços
│   ├── entregaveis/
│   ├── evidencias/
│   └── scripts/
└── projeto-integrador01/  # Política corporativa Hardening (DB-01)
    ├── entregaveis/
    ├── evidencias/
    └── scripts/
```

Em cada laboratório:

| Pasta | Conteúdo |
|-------|----------|
| `entregaveis/` | PDFs preenchidos (relatório e/ou Ordem de Serviço) |
| `evidencias/` | Logs, inventários e `shots/` (texto + imagens de terminal) |
| `scripts/` | Scripts `.sh` de execução e geradores `.py` dos PDFs |

---

## Laboratório 01 — Inventário Inicial de Segurança

**Objetivo:** estabelecer uma **baseline** do servidor sem alterar configurações, apenas observando e documentando o estado atual.

**Escopo:**

- identificação do SO, kernel, hostname e horário;
- inventário de usuários, grupos, serviços e portas;
- análise de rede, firewall, atualizações e logs;
- diagnóstico preliminar e lista de riscos;
- checklist e recomendações iniciais de hardening.

**Entregável principal:**

- `lab01/entregaveis/Lab01_Inventario_Inicial_Seguranca_PREENCHIDO.pdf`

**Conclusão resumida:** o ambiente “funcionava”, mas apresentava gaps clássicos de hardening (patches, firewall, política de senha, telemetria), reforçando que inventário deve anteceder qualquer intervenção.

---

## Laboratório 02 — Controle de Identidades e Privilégios

**Objetivo:** revisar identidades, grupos, permissões e privilégios administrativos, aplicando menor privilégio, segregação de funções e rastreabilidade.

**Escopo (7 missões):**

1. inventário das identidades;
2. organização de usuários e grupos corporativos;
3. revisão do grupo `sudo` e contas temporárias/serviço;
4. propriedade e permissões de diretórios (`/projetos`, `/financeiro`, `/auditoria`, `/infraestrutura`);
5. ACL excepcional (auditoria em `/financeiro`);
6. validação da política `sudo`;
7. auditoria final e parecer técnico.

**Entregáveis:**

- `lab02/entregaveis/Lab02_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab02/entregaveis/Lab02_Identidades_e_Privilegios_PREENCHIDO.pdf`

**Conclusão resumida:** identidades corporativas organizadas; `sudo` restrito a administradores; conta temporária bloqueada; conta de serviço sem login interativo; diretórios com política 750/770; ACL testada e removida; logging de `sudo` habilitado — **apto para operação** no escopo do lab.

---

## Laboratório 03 — Redução da Superfície de Ataque

**Objetivo:** reduzir componentes expostos, endurecer serviços essenciais e validar a postura de segurança com ferramentas de proteção e auditoria.

**Escopo (7 missões):**

1. inventário da superfície de ataque (serviços, portas, processos);
2. princípio da menor funcionalidade (desabilitar o que não é necessário);
3. hardening do SSH;
4. política de firewall com UFW (default deny);
5. proteção automatizada com Fail2Ban;
6. monitoramento de integridade com AIDE;
7. auditoria integrada com Lynis.

**Entregáveis:**

- `lab03/entregaveis/Lab03_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab03/entregaveis/Lab03_Reducao_Superficie_Ataque_PREENCHIDO.pdf`

**Resultados principais do ambiente de lab:**

- SSH endurecido (`PermitRootLogin no`, `X11Forwarding no`, restrição de usuários);
- UFW ativo com permissão explícita ao OpenSSH;
- Fail2Ban com jail `sshd`;
- AIDE com baseline completa (exclusão de mounts WSL `/mnt`);
- Lynis **Hardening Index = 69**.

**Parecer resumido:** controles do Lab 03 implementados; servidor **apto com pequenos ajustes** antes de produção (melhorias contínuas sugeridas pelo Lynis: SSH fino, política de senha, auditd, etc.).

---

## Laboratório 04A — Mandatory Access Control (SELinux e AppArmor)

**Objetivo:** validar a camada MAC do WEB-01 — identificar SELinux ou AppArmor, verificar estado operacional, interpretar contextos/perfis e emitir parecer comparativo antes da produção.

**Escopo:**

1. identificação do mecanismo MAC presente (LSM do kernel + ferramentas);
2. validação operacional (`sestatus` / `getenforce` ou `aa-status`);
3. contextos de arquivos (`ls -Z`) e processos (`ps -Z`);
4. restauração de labels (`restorecon`) e consulta de política (`semanage fcontext`);
5. bloco comparativo AppArmor (`aa-status`, `aa-enforce`, `aa-complain`, `aa-logprof`, `aa-genprof`);
6. tabela comparativa SELinux × AppArmor e parecer técnico.

**Resultados principais do ambiente de lab:**

- LSM do kernel com **SELinux** ativo;
- pacotes `selinux-utils`, `policycoreutils`, `selinux-policy-default` e `semanage-utils` instalados;
- **`sestatus` = enabled**, **`getenforce` = Enforcing**, política **default**;
- labels reais (`etc_t`, `shadow_t`, `sshd_exec_t`, `httpd_sys_content_t`);
- `restorecon` demonstrado (correção de label em `/etc/motd` e `/var/www/html`);
- `semanage fcontext` com **5843** regras;
- AppArmor (user-space) analisado para o comparativo do lab.

**Entregáveis:**

- `lab04a/entregaveis/Lab04A_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab04a/entregaveis/Lab04A_Mandatory_Access_Control_PREENCHIDO.pdf`

**Parecer resumido:** camada MAC validada com SELinux em Enforcing — **apto para operação** no escopo do Lab 04A. Próxima etapa: Lab 4B (manutenção contínua).

---

## Laboratório 04B — Manutenção Contínua do Hardening Linux

**Objetivo:** garantir que o WEB-01 permaneça seguro ao longo do ciclo de vida — atualização, vulnerabilidades, auditoria de configuração e integridade, com plano permanente e evidências.

**Escopo (4 etapas):**

1. atualização do SO (`apt update` / `list --upgradable` / `upgrade`);
2. gerenciamento de vulnerabilidades (`debsecan`; equivalentes a `ubuntu-security-status` / `dnf updateinfo`);
3. auditoria e integridade (`Lynis`, `AIDE`, `debsums`);
4. Plano Permanente de Manutenção + Checklist Operacional (Apêndice B).

**Resultados principais do ambiente de lab:**

- `apt update` OK (trixie + **trixie-security**);
- 1 atualização de segurança aplicada: **libexpat1** `2.8.2-1~deb13u1`;
- **debsecan:** 381 CVEs únicos (triagem; prioridade openssh/libc6);
- **Lynis Hardening Index = 69** (0 warnings, 48 suggestions);
- **AIDE:** diferenças vs baseline (esperado — labels SELinux do Lab 04A + upgrade);
- **debsums -c:** 0 inconsistências.

**Entregáveis:**

- `lab04b/entregaveis/Lab04B_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab04b/entregaveis/Lab04B_Manutencao_Continua_Hardening_PREENCHIDO.pdf`

**Parecer resumido:** ciclo de manutenção contínua executado e documentado — **apto para operação assistida**, com plano diário/semanal/mensal. Prepara o **Projeto Integrador (Aula 5)**.

---

## Projeto Integrador 01 — Política Corporativa de Hardening Linux

**Papel da equipe:** consultoria técnica da AmazonTech (não há roteiro fixo de comandos).

**Cenário escolhido:** **DB-01 — Servidor de Banco de Dados PostgreSQL** (distinto do WEB-01), com alta confidencialidade/integridade e acesso de rede restrito.

**Escopo do projeto técnico:**

1. caracterização do ambiente e levantamento de ativos;
2. análise de riscos;
3. política integrada (identidades, privilégios, serviços, SSH, firewall, MAC, patch, vulnerabilidades, auditoria, integridade, backup/PITR, documentação);
4. ferramentas selecionadas (apenas as necessárias);
5. plano de implantação (8 etapas) + manutenção contínua;
6. parecer, matriz de justificativa (Apêndice A) e checklist operacional.

**Base corporativa reutilizada:** princípios e controles validados nos Labs 01–04B do WEB-01, adaptados ao perfil de banco de dados (ex.: `5432/tcp` só para app-tier; backup/PITR).

**Entregáveis:**

- `projeto-integrador01/entregaveis/PI01_Ordem_de_Servico_PREENCHIDO.pdf`
- `projeto-integrador01/entregaveis/PI01_Projeto_Tecnico_Hardening_DB01_PREENCHIDO.pdf`

**Parecer resumido:** política **recomendada para implantação** no DB-01, como referência para demais servidores da AmazonTech.

---

## Laboratório 06A — Auditoria das Identidades do Windows

**Objetivo:** inventariar usuários, grupos, SIDs e Access Tokens no ambiente Windows (**WIN-ADM-01**), sem alterar configurações, como base para o Lab 06B (privilégios).

**Escopo (ferramentas):**

1. `whoami` / `whoami /user` / `whoami /groups` / `whoami /all`
2. `net user` e detalhamento de contas
3. `net localgroup` (foco em **Administradores**)
4. `lusrmgr.msc` (equivalente PowerShell `Get-LocalUser` / `Get-LocalGroup`)
5. `Get-LocalUser` para auditoria automatizada
6. parecer e recomendações de reorganização

**Resultados principais do ambiente de lab (MachadoPC):**

- **6** contas locais; habilitadas: `marge`, `postgres`
- desabilitadas: Administrador, Convidado, DefaultAccount, WDAGUtilityAccount
- grupo **Administradores:** `Administrador` + `marge`
- SID de `marge`: `S-1-5-21-…-1001`
- sessão com token UAC filtrado (integridade média)
- auditoria **somente leitura** (nenhuma alteração)

**Entregáveis:**

- `lab06a/entregaveis/Lab06A_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab06a/entregaveis/Lab06A_Identidades_Windows_PREENCHIDO.pdf`

**Parecer resumido:** auditoria concluída — **apto para avançar ao Lab 06B**, com recomendações (separar conta diária/admin, documentar `postgres`, grupos organizacionais).

---

## Laboratório 06B — Auditoria dos Privilégios Administrativos

**Objetivo:** verificar **quais ações** as identidades podem executar no Windows (privilégios / User Rights / Access Token), alinhado ao **menor privilégio**, sem alterar configurações.

**Escopo (ferramentas):**

1. `whoami /priv` — privilégios no token
2. `secpol.msc` / `secedit` — User Rights Assignment
3. `gpedit.msc` + políticas UAC
4. `whoami /all` — correlação identidade/grupos/privilégios
5. PowerShell (`Get-Command *Security*`, grupos admin)
6. MMC (snap-ins)
7. Event Viewer / `Get-WinEvent`
8. consolidação e recomendações

**Resultados principais (MachadoPC / WIN-ADM-01):**

- token filtrado UAC: **5** privilégios listados; **1 ativo** (`SeChangeNotifyPrivilege`)
- `SeShutdownPrivilege` presente porém **Desativado** na sessão média
- **UAC** ativo (`EnableLUA=1`, `ConsentPromptBehaviorAdmin=5`)
- `gpedit`/`secpol` **ausentes** no Windows 11 Home; `secedit` exige elevação
- log **Security** inacessível sem admin; System/Application OK
- auditoria **somente leitura**

**Entregáveis:**

- `lab06b/entregaveis/Lab06B_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab06b/entregaveis/Lab06B_Privilegios_Administrativos_PREENCHIDO.pdf`

**Parecer resumido:** auditoria concluída — **apto para o Lab 06C (NTFS)**; menor privilégio parcial (UAC ajuda, mas `marge` permanece em Administradores).

---

## Laboratório 06C — Auditoria das Permissões NTFS

**Objetivo:** verificar **quais recursos** as identidades podem acessar (ACL/DACL, herança, permissões efetivas), alinhado a need-to-know, **sem alterar ACL**.

**Escopo (ferramentas):**

1. Explorer → Segurança (equiv. `Get-Acl`)
2. Segurança avançada (owner, herança, ACE)
3. Effective Access (equiv.)
4. `icacls`
5. `Get-Acl` / `Get-ChildItem`
6. comparação GUI × CLI + consolidação

**Resultados principais (árvore simulada `AmazonTech`):**

- pastas: Financeiro, Projetos, Auditoria, TI, Compartilhado
- **Financeiro:** herança ativa; `Administradores (F)`, `SYSTEM (F)`, **`Usuários autenticados (M)`**, `Usuários (RX)`
- mesmo perfil amplo em pastas “sensíveis” e “compartilhadas” → falta segregação
- GUI/`icacls`/`Get-Acl` **consistentes**
- auditoria **somente leitura** (ACL não modificadas)

**Entregáveis:**

- `lab06c/entregaveis/Lab06C_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab06c/entregaveis/Lab06C_Permissoes_NTFS_PREENCHIDO.pdf`

**Parecer resumido:** auditoria concluída — **apto para Governança / Security Baselines**; reorganizar ACL (grupos departamentais, restringir Auth Users) em janela autorizada.

---

## Laboratório 06D — Governança e Security Baselines

**Objetivo:** garantir que a arquitetura de segurança **permaneça padronizada** ao longo do tempo via Security Baselines, LGPO/GPO, MMC/SCA e um **Plano Corporativo de Governança** (sem alterar políticas nesta OS).

**Escopo:**

1. Microsoft Security Compliance Toolkit (conceito/baseline Win11)
2. LGPO.exe (export/import/aplicação de políticas locais)
3. gpedit.msc / MMC (administração centralizada)
4. Security Configuration and Analysis (comparar host × baseline)
5. consolidação de drifts dos Labs 06A–06C
6. Plano Corporativo de Governança (objetivo, ferramentas, periodicidade, indicadores)

**Resultados principais:**

- UAC ativo (`EnableLUA=1`); gpedit/secpol **ausentes** (Windows 11 Home)
- SCT/LGPO **não instalados** no host — recomenda-se adoção corporativa
- Drifts: admin diário; NTFS Auth Users; falta baseline aplicada
- Plano com auditorias diária→trimestral e KPIs de conformidade

**Entregáveis:**

- `lab06d/entregaveis/Lab06D_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab06d/entregaveis/Lab06D_Governanca_Security_Baselines_PREENCHIDO.pdf`
- `lab06d/evidencias/docs/Plano_Corporativo_Governanca_AmazonTech.txt`

**Parecer resumido:** ciclo **06A–06D concluído** (auditoria + planejamento) — **apto para implantação do Plano de Governança** mediante aceite da Diretoria.

---

## Laboratório 07A — Microsoft Defender

**Objetivo:** validar a configuração do Microsoft Defender como **primeira camada** da proteção de endpoints Windows (sem alterar configurações críticas permanentes).

**Escopo:**

1. localizar Windows Security e serviços do Defender
2. verificar proteção em tempo real, nuvem, amostras e Tamper Protection
3. atualizações de inteligência de segurança
4. análise rápida (QuickScan) e tipos de verificação
5. histórico de proteção / ameaças
6. consulta administrativa `Get-MpComputerStatus`

**Resultados principais:**

- WinDefend/MdCoreSvc ativos; RTP, IOAV, Behavior, NIS e Tamper Protection **habilitados**
- Assinaturas atualizadas (`1.457.40.0`, idade 0 dias) após `Update-MpSignature`
- QuickScan ~373 s concluído; histórico com detecções passadas tratadas (sem ameaça ativa)
- Controlled Folder Access e PUAProtection ativos

**Entregáveis:**

- `lab07a/entregaveis/Lab07A_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab07a/entregaveis/Lab07A_Microsoft_Defender_PREENCHIDO.pdf`

**Parecer resumido:** endpoint **apto para homologação da camada Microsoft Defender**, com recomendações de padronização corporativa (Intune/GPO, FullScan, MDE).

---

## Laboratório 07B — Windows Defender Firewall

**Objetivo:** validar a configuração do Windows Defender Firewall como camada de controle das **comunicações** do endpoint (sem alterar regras permanentemente).

**Escopo:**

1. perfis Domain / Private / Public
2. console avançado (`wf.msc`) e inventário de regras
3. interpretação de regras de entrada e saída
4. consultas PowerShell (`Get-NetFirewallProfile`, `Get-NetFirewallRule`)
5. exploração da exportação de política (`.wfw`)

**Resultados principais:**

- Três perfis **Enabled=True**; rede ativa classificada como **Public**
- MpsSvc Running; **552** regras (312 habilitadas); IPsec = 0
- Amostra documentada: IPv6-Entrada (Inbound) + SSDP-Saída (Outbound)
- Export `.wfw` identificado; execução exige elevação (limitação registrada)

**Entregáveis:**

- `lab07b/entregaveis/Lab07B_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab07b/entregaveis/Lab07B_Windows_Firewall_PREENCHIDO.pdf`

**Parecer resumido:** endpoint **apto para homologação da camada Firewall**, com revisão periódica de exceções e logging.

---

## Laboratório 07C — BitLocker

**Objetivo:** validar BitLocker/TPM para proteção de dados **em repouso** (sem habilitar criptografia nesta OS).

**Escopo:**

1. disponibilidade do BitLocker na edição do Windows
2. verificação do TPM (`tpm.msc` / PnP)
3. estado das unidades (`manage-bde -status`)
4. cmdlets administrativos (`Get-Command *BitLocker*`, `Get-BitLockerVolume`)
5. exploração das opções de chave de recuperação

**Resultados principais:**

- Windows 11 **Home**: UI completa ausente; `manage-bde`/módulo BitLocker/Device Encryption presentes
- **TPM 2.0** presente (PnP OK); `Get-Tpm`/`manage-bde -status` exigem elevação
- 15 cmdlets BitLocker listados; BDESVC Stopped/Manual
- Nenhuma criptografia ativada (restricao da OS)

**Entregáveis:**

- `lab07c/entregaveis/Lab07C_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab07c/entregaveis/Lab07C_BitLocker_PREENCHIDO.pdf`

**Parecer resumido:** auditoria concluída — **apto com ressalvas** (upgrade Pro/Enterprise ou Device Encryption + custódia de recovery key antes da política obrigatória).

---

## Laboratório 07D — Administração Segura com PowerShell

**Objetivo:** validar o PowerShell como plataforma de administração **segura, padronizada e auditável** (somente consultas; sem alterar configurações permanentes).

**Escopo:**

1. ambiente / versão PowerShell e Windows Terminal
2. `Get-Help` / `Get-Command`
3. `Get-Service` / `Get-Process`
4. Execution Policy (`Get-ExecutionPolicy -List`)
5. `Get-ComputerInfo` + integração com Defender/Firewall (Labs 07A/07B)

**Resultados principais:**

- PowerShell **5.1.26100.8875** (Desktop); Windows Terminal disponível
- ~1731 comandos visíveis; CurrentUser **RemoteSigned**
- Process=Bypass apenas na sessão de captura (não permanente)
- Integração confirmada: `Get-MpComputerStatus` + `Get-NetFirewallProfile`

**Entregáveis:**

- `lab07d/entregaveis/Lab07D_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab07d/entregaveis/Lab07D_PowerShell_PREENCHIDO.pdf`

**Parecer resumido:** ciclo **07A–07D concluído** — PowerShell **apto** como plataforma de administração segura para playbooks autorizados.

---

## Laboratório 07E — Hardening de Serviços

**Objetivo:** avaliar a configuração do endpoint sob a ótica do Hardening (superfície de ataque), elaborando um plano preliminar **sem desabilitar** serviços.

**Escopo:**

1. inventário de serviços (`services.msc` / `Get-Service`)
2. programas de inicialização automática
3. recursos opcionais do Windows
4. consultas PowerShell complementares
5. plano preliminar de Hardening (tabela)

**Resultados principais:**

- **291** serviços (126 Running; RemoteRegistry já Disabled; WinDefend OK; Spooler a revisar)
- Startup: Teams, Adobe Sync, Edge, SecurityHealth, PDF24
- Superfície extra: AdobeARM, PDF24, PostgreSQL, VMware, WSL (Automatic)
- Optional Features: listagem completa exige elevação (limitação registrada)

**Entregáveis:**

- `lab07e/entregaveis/Lab07E_Ordem_de_Servico_PREENCHIDO.pdf`
- `lab07e/entregaveis/Lab07E_Hardening_Servicos_PREENCHIDO.pdf`
- `lab07e/evidencias/docs/Plano_Preliminar_Hardening_Servicos.txt`

**Parecer resumido:** ciclo **07A–07E concluído** — avaliação de Hardening **apta**; implantação do plano mediante aceite da Diretoria.

---

## Princípios aplicados

1. **Menor privilégio** — apenas o acesso necessário à função.
2. **Menor funcionalidade** — desativar o que não tem justificativa operacional.
3. **Menor comunicação** — firewall permitindo só o tráfego necessário.
4. **Defesa em profundidade** — SSH + UFW + Fail2Ban + AIDE + MAC (SELinux) + auditoria.
5. **Evidência antes de opinião** — conclusões ancoradas em saídas de comando.
6. **Manutenção contínua** — atualizar, auditar e monitorar integridade em ciclo permanente.

---

## Como regenerar os PDFs (opcional)

Requer Python 3 com `reportlab` e `Pillow`.

```powershell
# Lab 01
python lab01\scripts\generate_lab01_with_shots.py

# Lab 02
python lab02\scripts\generate_lab02_with_shots.py

# Lab 03
python lab03\scripts\generate_lab03_pdfs.py

# Lab 04A
python lab04a\scripts\generate_lab04a_pdfs.py

# Lab 04B
python lab04b\scripts\generate_lab04b_pdfs.py

# Projeto Integrador 01
python projeto-integrador01\scripts\generate_pi01_pdfs.py

# Lab 06A
python lab06a\scripts\generate_lab06a_pdfs.py

# Lab 06B
python lab06b\scripts\generate_lab06b_pdfs.py

# Lab 06C
python lab06c\scripts\generate_lab06c_pdfs.py

# Lab 06D
python lab06d\scripts\generate_lab06d_pdfs.py

# Lab 07A
python lab07a\scripts\generate_lab07a_pdfs.py

# Lab 07B
python lab07b\scripts\generate_lab07b_pdfs.py

# Lab 07C
python lab07c\scripts\generate_lab07c_pdfs.py

# Lab 07D
python lab07d\scripts\generate_lab07d_pdfs.py

# Lab 07E
python lab07e\scripts\generate_lab07e_pdfs.py
```

Os PDFs são gravados em `*/entregaveis/` (e uma cópia pode ser enviada também para Downloads, conforme o script).

---

## Observações

- Os laboratórios foram executados em **ambiente de laboratório (WSL/Debian)**, não em produção real.
- Nenhuma alteração deve ser reproduzida em servidores corporativos sem autorização e janela de mudança.
- Hardening é tratado como **processo contínuo**, não como atividade pontual de implantação.
