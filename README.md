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
└── lab03/                 # Redução da Superfície de Ataque
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

## Princípios aplicados

1. **Menor privilégio** — apenas o acesso necessário à função.
2. **Menor funcionalidade** — desativar o que não tem justificativa operacional.
3. **Menor comunicação** — firewall permitindo só o tráfego necessário.
4. **Defesa em profundidade** — SSH + UFW + Fail2Ban + AIDE + auditoria.
5. **Evidência antes de opinião** — conclusões ancoradas em saídas de comando.

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
```

Os PDFs são gravados em `*/entregaveis/` (e uma cópia pode ser enviada também para Downloads, conforme o script).

---

## Observações

- Os laboratórios foram executados em **ambiente de laboratório (WSL/Debian)**, não em produção real.
- Nenhuma alteração deve ser reproduzida em servidores corporativos sem autorização e janela de mudança.
- Hardening é tratado como **processo contínuo**, não como atividade pontual de implantação.
