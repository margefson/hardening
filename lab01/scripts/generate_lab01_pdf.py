#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o PDF de entrega do Lab 01 - Inventário Inicial de Segurança."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem
)

OUTPUT = r"d:\MMB\workspace\hardening\lab01\entregaveis\Lab01_Inventario_Inicial_Seguranca_PREENCHIDO.pdf"

PRIMARY = HexColor("#1a365d")
ACCENT = HexColor("#2c5282")
LIGHT = HexColor("#edf2f7")
WARN = HexColor("#c05621")
OK = HexColor("#276749")
BORDER = HexColor("#cbd5e0")


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle", fontName="Helvetica-Bold", fontSize=20,
        textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=8, leading=26
    ))
    styles.add(ParagraphStyle(
        name="CoverSub", fontName="Helvetica", fontSize=12,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=6, leading=16
    ))
    styles.add(ParagraphStyle(
        name="H1Doc", fontName="Helvetica-Bold", fontSize=14,
        textColor=PRIMARY, spaceBefore=14, spaceAfter=8, leading=18
    ))
    styles.add(ParagraphStyle(
        name="H2Doc", fontName="Helvetica-Bold", fontSize=11,
        textColor=ACCENT, spaceBefore=10, spaceAfter=5, leading=14
    ))
    styles.add(ParagraphStyle(
        name="BodyJust", fontName="Helvetica", fontSize=9.5,
        alignment=TA_JUSTIFY, spaceAfter=6, leading=13
    ))
    styles.add(ParagraphStyle(
        name="BodyLeft", fontName="Helvetica", fontSize=9.5,
        alignment=TA_LEFT, spaceAfter=4, leading=13
    ))
    styles.add(ParagraphStyle(
        name="Evidence", fontName="Courier", fontSize=8,
        textColor=HexColor("#1a202c"), backColor=LIGHT,
        leftIndent=4, rightIndent=4, spaceBefore=3, spaceAfter=6, leading=11
    ))
    styles.add(ParagraphStyle(
        name="Meta", fontName="Helvetica", fontSize=9,
        textColor=HexColor("#4a5568"), alignment=TA_CENTER, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name="QTitle", fontName="Helvetica-Bold", fontSize=10,
        textColor=PRIMARY, spaceBefore=8, spaceAfter=3, leading=13
    ))
    styles.add(ParagraphStyle(
        name="Small", fontName="Helvetica", fontSize=8.5,
        textColor=HexColor("#4a5568"), alignment=TA_JUSTIFY, spaceAfter=4, leading=11
    ))
    styles.add(ParagraphStyle(
        name="BulletText", fontName="Helvetica", fontSize=9.5,
        leftIndent=12, spaceAfter=3, leading=12
    ))
    styles.add(ParagraphStyle(
        name="TableCell", fontName="Helvetica", fontSize=8.5, leading=11
    ))
    styles.add(ParagraphStyle(
        name="TableHead", fontName="Helvetica-Bold", fontSize=8.5,
        textColor=white, leading=11
    ))
    return styles


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(1.2)
    canvas.line(1.8 * cm, A4[1] - 1.3 * cm, A4[0] - 1.8 * cm, A4[1] - 1.3 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(ACCENT)
    canvas.drawString(1.8 * cm, A4[1] - 1.1 * cm, "AmazonTech Indústria 4.0 — Lab 01 | Inventário Inicial de Segurança")
    canvas.drawRightString(A4[0] - 1.8 * cm, A4[1] - 1.1 * cm, "Windows e Linux Hardening")
    canvas.line(1.8 * cm, 1.4 * cm, A4[0] - 1.8 * cm, 1.4 * cm)
    canvas.drawCentredString(A4[0] / 2, 0.9 * cm, f"Página {doc.page} | Diagnóstico técnico baseado em evidências | 28/07/2026")
    canvas.restoreState()


def kv_table(rows, styles, col1=4.2 * cm, col2=12.3 * cm):
    data = []
    for k, v in rows:
        data.append([
            Paragraph(f"<b>{k}</b>", styles["TableCell"]),
            Paragraph(str(v), styles["TableCell"]),
        ])
    t = Table(data, colWidths=[col1, col2])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def checklist_table(items, styles):
    head = [
        Paragraph("Item", styles["TableHead"]),
        Paragraph("Status", styles["TableHead"]),
        Paragraph("Evidência / Observação", styles["TableHead"]),
    ]
    data = [head]
    for item, status, obs in items:
        data.append([
            Paragraph(item, styles["TableCell"]),
            Paragraph(status, styles["TableCell"]),
            Paragraph(obs, styles["TableCell"]),
        ])
    t = Table(data, colWidths=[5.2 * cm, 2.2 * cm, 9.1 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
    ]))
    return t


def risk_table(rows, styles):
    head = [
        Paragraph("Risco", styles["TableHead"]),
        Paragraph("Severidade", styles["TableHead"]),
        Paragraph("Evidência técnica", styles["TableHead"]),
    ]
    data = [head]
    for r, s, e in rows:
        data.append([
            Paragraph(r, styles["TableCell"]),
            Paragraph(s, styles["TableCell"]),
            Paragraph(e, styles["TableCell"]),
        ])
    t = Table(data, colWidths=[4.5 * cm, 2.5 * cm, 9.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), WARN),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
    ]))
    return t


def build():
    styles = make_styles()
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.9 * cm,
        title="Lab 01 - Inventário Inicial de Segurança (Preenchido)",
        author="Equipe de Segurança — AmazonTech",
    )
    story = []

    # ========== CAPA ==========
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("LABORATÓRIO 1", styles["CoverSub"]))
    story.append(Paragraph("Inventário Inicial de Segurança", styles["CoverTitle"]))
    story.append(Paragraph("Documento de Entrega — Completo e Preenchido", styles["CoverSub"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("<b>Disciplina:</b> Windows e Linux Hardening", styles["Meta"]))
    story.append(Paragraph("<b>Aula:</b> 1 — Inventário Inicial de Segurança", styles["Meta"]))
    story.append(Paragraph("<b>Cliente:</b> AmazonTech Indústria 4.0", styles["Meta"]))
    story.append(Paragraph("<b>Papel:</b> Analistas de Segurança / Consultores de Hardening / Auditores Técnicos", styles["Meta"]))
    story.append(Paragraph("<b>Data da coleta:</b> 28/07/2026 — 18:35 (America/Manaus)", styles["Meta"]))
    story.append(Paragraph("<b>Ambiente analisado:</b> Debian GNU/Linux 13 (trixie) — hostname MachadoPC", styles["Meta"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Este relatório consolida os quatro entregáveis exigidos: (1) Inventário Técnico, "
        "(2) Diagnóstico Inicial, (3) Lista preliminar de riscos e (4) Plano de investigação. "
        "Todas as conclusões estão ancoradas nas evidências coletadas no terminal; nenhuma "
        "configuração foi alterada durante a execução deste laboratório.",
        styles["BodyJust"]
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "<b>Comandos utilizados (amostra):</b> cat /etc/os-release · uname -a · hostnamectl · "
        "getent passwd/group · systemctl list-units · ss -tulnp · ip -br addr · apt list --upgradable · "
        "journalctl · ls /var/log · timedatectl",
        styles["Small"]
    ))

    story.append(PageBreak())

    # ========== DOC 1: INVENTÁRIO ==========
    story.append(Paragraph("DOCUMENTO 1 — Inventário Técnico", styles["H1Doc"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

    story.append(Paragraph("1. Identificação do Ambiente (Anexo A)", styles["H2Doc"]))
    story.append(kv_table([
        ("Nome da equipe", "Equipe de Segurança AmazonTech (Analistas / Hardening / Auditoria)"),
        ("Data", "28/07/2026"),
        ("Distribuição Linux", "Debian GNU/Linux 13 (trixie)"),
        ("Versão", "VERSION_ID=13 · DEBIAN_VERSION_FULL=13.0 · codename trixie"),
        ("Kernel", "6.6.114.1-microsoft-standard-WSL2 (x86_64) — Linux MachadoPC"),
        ("Hostname", "MachadoPC (Static hostname: MachadoPC · Virtualization: wsl)"),
        ("Data/hora do sistema", "Tue Jul 28 18:35:30 -04 2026 · UTC 22:35:30 · TZ America/Manaus"),
        ("Sincronização de relógio", "System clock synchronized: yes · NTP service: n/a"),
        ("Uptime na coleta", "≈ 1 minuto (sistema recém-inicializado no momento da coleta)"),
    ], styles))

    story.append(Paragraph("Reflexão — Etapa 1 (Sistema)", styles["H2Doc"]))
    story.append(Paragraph(
        "<b>O sistema está atualizado?</b> Não. Foi identificada lista de pacotes atualizáveis "
        "(31 entradas em <font face='Courier'>apt list --upgradable</font>), incluindo componentes "
        "críticos: <font face='Courier'>libc6</font>, <font face='Courier'>systemd</font>, "
        "<font face='Courier'>sudo</font>, <font face='Courier'>bash</font>, "
        "<font face='Courier'>dpkg</font> e <font face='Courier'>tzdata</font>.",
        styles["BodyJust"]
    ))
    story.append(Paragraph(
        "<b>A versão ainda possui suporte?</b> Sim, sob a ótica da distribuição: Debian 13 (trixie) "
        "é a versão estável atual (stable) no momento da coleta, portanto ainda possui suporte "
        "oficial de segurança da Debian. Contudo, o kernel observado "
        "(<font face='Courier'>microsoft-standard-WSL2</font>) indica plataforma WSL, o que "
        "deve ser confrontado com a política corporativa de hospedagem em produção.",
        styles["BodyJust"]
    ))
    story.append(Paragraph(
        "<b>O Kernel é compatível com a política de atualização da organização?</b> "
        "Há divergência potencial: o inventário registra kernel Microsoft WSL2, não um kernel "
        "genérico de servidor Debian bare-metal/VM tradicional. Antes de declarar conformidade, "
        "é necessário obter a política formal de atualização e o escopo aceito de hipervisores "
        "pela AmazonTech. Evidência: saída de <font face='Courier'>uname -a</font> e "
        "<font face='Courier'>hostnamectl</font> (Virtualization: wsl).",
        styles["BodyJust"]
    ))

    story.append(Paragraph("2. Usuários e Grupos", styles["H2Doc"]))
    story.append(Paragraph(
        "<b>Usuários com shell de login:</b> root (UID 0, /bin/bash); machado (UID 1000, /bin/bash); "
        "sync (UID 4, /bin/sync — conta de sistema).",
        styles["BodyLeft"]
    ))
    story.append(Paragraph(
        "<b>Conta administrativa humana:</b> machado ∈ grupos sudo, adm, cdrom, dip, plugdev, users.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph(
        "<b>Contas de serviço / sistema (amostra):</b> daemon, bin, sys, www-data, backup, _apt, "
        "systemd-network, dhcpcd, messagebus, nobody — majoritariamente com /usr/sbin/nologin ou /bin/false.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph(
        "<b>Única conta UID 0:</b> root. Sessão ativa na coleta: machado em pts/1.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph("Reflexão — Etapa 2", styles["H2Doc"]))
    story.append(Paragraph(
        "• <b>Usuários que não deveriam estar presentes?</b> Não há evidência de contas humanas "
        "órfãs além de root e machado. Contas de serviço aparentam ser padrão da instalação Debian. "
        "A conta games existe com nologin (padrão Debian) — baixa relevância operacional.<br/>"
        "• <b>Excesso de contas privilegiadas?</b> Não excessivo: apenas root (UID 0) e um usuário "
        "no grupo sudo (machado). Porém, a existência de sudo sem inventário de regras em "
        "/etc/sudoers.d (acesso negado sem senha na coleta) impede afirmar o princípio do menor privilégio.<br/>"
        "• <b>Contas sem finalidade aparente?</b> Nenhuma conta humana sem finalidade aparente "
        "foi identificada; contas de serviço seguem o padrão do sistema.",
        styles["BodyJust"]
    ))

    story.append(Paragraph("3. Serviços", styles["H2Doc"]))
    story.append(Paragraph(
        "<b>Serviços ativos (running):</b> cron, dbus, getty@tty1, systemd-hostnamed, "
        "systemd-journald, systemd-logind, systemd-timedated, systemd-udevd, user@1000.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph(
        "<b>Serviços enabled:</b> cron, e2scrub_reap, getty@, networking, systemd-pstore.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph(
        "<b>Observação crítica:</b> openssh-server <b>não instalado</b> (dpkg: un / none). "
        "sshd inactive/not-found. fail2ban não encontrado. unattended-upgrades não instalado.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph("Reflexão — Etapa 3", styles["H2Doc"]))
    story.append(Paragraph(
        "• A superfície de serviços locais é relativamente enxuta para um host mínimo.<br/>"
        "• getty@tty1 e login local estão ativos — esperado em console.<br/>"
        "• cron.service enabled amplia superfície se jobs desconhecidos existirem — necessita "
        "revisão de crontabs nas próximas aulas.<br/>"
        "• Ausência de SSH reduz exposição remota agora, mas também limita administração remota "
        "segura quando o servidor for colocado em rede corporativa — item a planejar, não a improvisar.",
        styles["BodyJust"]
    ))

    story.append(PageBreak())
    story.append(Paragraph("4. Rede e Exposição", styles["H2Doc"]))
    story.append(kv_table([
        ("Interfaces", "lo (127.0.0.1/8; 10.255.255.254/32) · eth0 UP (172.28.32.117/20 + IPv6 link-local)"),
        ("Rota padrão", "default via 172.28.32.1 dev eth0"),
        ("Portas em escuta", "UDP 127.0.0.1:323 · UDP/TCP 10.255.255.254:53 · UDP [::1]:323"),
        ("Firewall UFW", "Comando ufw presente, porém status não obtido (sudo requer senha). Sem evidência de regras ativas."),
        ("iptables / nft", "Sem saída acessível sem privilégio elevado — estado do firewall host não comprovado."),
    ], styles))
    story.append(Paragraph("Reflexão — Etapa 4", styles["H2Doc"]))
    story.append(Paragraph(
        "• <b>Portas necessárias:</b> No estado atual, não há serviço de aplicação corporativa em escuta "
        "em 0.0.0.0. A porta 53 em 10.255.255.254 está associada ao ambiente WSL (resolução DNS interna). "
        "Porta 323 local sugere chrony/NTP control socket local.<br/>"
        "• <b>Serviços acessíveis sem necessidade?</b> Não há evidência de SSH, HTTP, banco ou painel "
        "expostos. Isso é positivo para a superfície atual, mas insuficiente para declarar produção segura.<br/>"
        "• <b>Firewall coerente?</b> Não é possível afirmar. Não há evidência de UFW ativo nem de "
        "regras iptables/nft listadas. Para produção, ausência de política de firewall documentada "
        "é risco de configuração omissa.",
        styles["BodyJust"]
    ))

    story.append(Paragraph("5. Atualizações e Logs", styles["H2Doc"]))
    story.append(Paragraph(
        "<b>Atualizações pendentes:</b> 31 pacotes upgradable (evidência em apt list --upgradable), "
        "incluindo sudo, systemd, libc6, bash, dpkg, udev, tzdata.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph(
        "<b>Política de senha (/etc/login.defs):</b> PASS_MAX_DAYS=99999 · PASS_MIN_DAYS=0 · "
        "PASS_WARN_AGE=7 — senhas efetivamente sem expiração máxima prática.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph(
        "<b>Mecanismo de logs:</b> systemd-journald ativo; rsyslog inactive. Arquivos em /var/log: "
        "alternatives.log, apt/, bootstrap.log, btmp, dpkg.log, journal/, lastlog, wtmp. "
        "Uso de journal ≈ 64M. auth.log tradicional ausente/sem entradas via journalctl -u ssh.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph(
        "<b>Erros recentes no journal:</b> mensagens WSL/PCI/dxg e CheckConnection getaddrinfo failed; "
        "falhas de unmount de /init e /tmp/.X11-unix no desligamento. Não há evidência clara de "
        "intrusão; há indícios de ruído típico de ambiente WSL e possível instabilidade de rede no boot.",
        styles["BodyLeft"]
    ))
    story.append(Paragraph("Reflexão — Etapa 5", styles["H2Doc"]))
    story.append(Paragraph(
        "• <b>Falhas recentes?</b> Sim, erros de kernel/WSL e falha de resolução DNS no boot "
        "(getaddrinfo failed). Não há evidência de autenticação suspeita nos logs acessíveis.<br/>"
        "• <b>Registros suficientes para auditoria?</b> Parcialmente. journald está ativo, porém "
        "rsyslog está inativo, não há auth.log clássico populado e não há evidência de encaminhamento "
        "centralizado de logs — insuficiente para auditoria externa rigorosa.<br/>"
        "• <b>Sinais de configuração inadequada?</b> Sim: atualizações pendentes; PASS_MAX_DAYS=99999; "
        "ausência de unattended-upgrades; firewall não evidenciado; NTP service = n/a apesar do clock synced.",
        styles["BodyJust"]
    ))

    story.append(Paragraph("6. Checklist do Inventário", styles["H2Doc"]))
    story.append(checklist_table([
        ("Distribuição Linux identificada", "☑ Sim", "Debian GNU/Linux 13 (trixie)"),
        ("Versão do Kernel registrada", "☑ Sim", "6.6.114.1-microsoft-standard-WSL2"),
        ("Hostname identificado", "☑ Sim", "MachadoPC"),
        ("Usuários listados", "☑ Sim", "root, machado + contas de sistema"),
        ("Grupos identificados", "☑ Sim", "sudo, adm, users, etc."),
        ("Contas administrativas verificadas", "☑ Sim", "root + machado∈sudo"),
        ("Serviços ativos registrados", "☑ Sim", "9 units running"),
        ("Portas abertas identificadas", "☑ Sim", "53 (WSL DNS), 323 (local)"),
        ("Interfaces de rede documentadas", "☑ Sim", "lo, eth0 172.28.32.117/20"),
        ("Firewall analisado", "☑ Parcial", "Sem regras evidenciadas (falta privilégio sudo)"),
        ("Atualizações verificadas", "☑ Sim", "31 pacotes pendentes"),
        ("Logs localizados", "☑ Sim", "journald ativo; /var/log inventariado"),
    ], styles))

    story.append(PageBreak())

    # ========== DOC 2: DIAGNÓSTICO ==========
    story.append(Paragraph("DOCUMENTO 2 — Diagnóstico Inicial", styles["H1Doc"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
    story.append(Paragraph(
        "Com base exclusivamente nas evidências coletadas, o ambiente apresenta uma instalação "
        "Debian mínima com baixa exposição de serviços de rede no momento da coleta, porém "
        "<b>não atende</b> a um padrão mínimo de prontidão para produção sob auditoria externa. "
        "Os principais achados são: (a) dívida de atualizações em pacotes de segurança/base; "
        "(b) ausência de controles evidentes de firewall; (c) política de senha excessivamente "
        "permissiva; (d) logging incompleto para auditoria; (e) plataforma WSL cujo enquadramento "
        "em produção corporativa precisa ser validado pela diretoria.",
        styles["BodyJust"]
    ))

    story.append(Paragraph("Questão 1 — Quais componentes representam maior potencial de risco?", styles["QTitle"]))
    story.append(Paragraph(
        "1) <b>Pacotes desatualizados</b> (sudo, systemd, libc6, bash, dpkg) — elevam probabilidade "
        "de exploração de CVEs conhecidas. Evidência: apt list --upgradable (31 itens).<br/>"
        "2) <b>Firewall não evidenciado</b> — qualquer serviço futuro exposto herdará ausência de "
        "controle de tráfego. Evidência: sem regras UFW/iptables/nft acessíveis/confirmadas.<br/>"
        "3) <b>Política de senha PASS_MAX_DAYS=99999</b> — credenciais privilegiadas (root/machado∈sudo) "
        "sem ciclo de rotação. Evidência: /etc/login.defs.<br/>"
        "4) <b>Conta privilegiada local (machado∈sudo)</b> sem inventário completo de sudoers — "
        "risco de privilégio excessivo se regras forem amplas. Evidência: getent group sudo; "
        "sudoers.d inacessível sem senha.<br/>"
        "5) <b>Lacuna de telemetria de autenticação</b> — rsyslog inactive e ausência de trilha auth "
        "robusta dificultam detecção e resposta. Evidência: systemctl is-active rsyslog=inactive.",
        styles["BodyJust"]
    ))

    story.append(Paragraph("Questão 2 — Quais informações ainda seriam necessárias antes de iniciar o hardening?", styles["QTitle"]))
    story.append(Paragraph(
        "• Inventário de aplicações/serviços de negócio previstos (web, banco, agentes).<br/>"
        "• Política formal de atualização, retenção de logs e classificação do ativo (produção/dev).<br/>"
        "• Confirmação se WSL é aceito como plataforma de produção ou se haverá migração para VM/bare-metal.<br/>"
        "• Conteúdo de /etc/sudoers e /etc/sudoers.d (requer privilégio).<br/>"
        "• Estado completo do firewall (ufw/iptables/nft) e topologia de rede corporativa.<br/>"
        "• Requisitos da auditoria externa (controles CIS, ISO 27001, checklist específico).<br/>"
        "• Baseline de contas aprovadas (RBAC) e método de autenticação desejado (SSH keys, MFA).<br/>"
        "• Crontabs, timers systemd e pacotes instalados completos (dpkg -l).",
        styles["BodyJust"]
    ))

    story.append(Paragraph("Questão 3 — Existe alguma evidência de configuração inadequada?", styles["QTitle"]))
    story.append(Paragraph(
        "<b>Sim, com evidência:</b><br/>"
        "• Atualizações pendentes em componentes críticos (apt list --upgradable).<br/>"
        "• PASS_MAX_DAYS=99999 em /etc/login.defs.<br/>"
        "• Pacote unattended-upgrades não instalado (sem manutenção automática evidenciada).<br/>"
        "• rsyslog inactive — dependência exclusiva de journald local sem evidência de retenção/encaminhamento.<br/>"
        "• NTP service = n/a (timedatectl), embora o relógio esteja sincronizado — controle de tempo "
        "não está claramente gerido por serviço NTP local auditável.<br/>"
        "• Firewall sem evidência de política aplicada.",
        styles["BodyJust"]
    ))

    story.append(Paragraph("Questão 4 — O ambiente pode ser considerado pronto para produção? Justifique.", styles["QTitle"]))
    story.append(Paragraph(
        "<b>Não.</b> Embora a superfície de escuta atual seja reduzida (sem SSH/HTTP expostos) e "
        "não existam indícios de incidente nos logs acessíveis, a prontidão para produção exige "
        "controles mínimos demonstráveis: patches aplicados, firewall com política explícita, "
        "gestão de identidade/senha alinhada a política, logging auditável e plataforma homologada. "
        "Nenhum desses pilares está plenamente evidenciado neste inventário. Declarar o servidor "
        "“seguro porque está funcionando e sem incidentes recentes”, como sugerido no briefing da "
        "diretoria, <b>não encontra suporte técnico</b> nas evidências coletadas.",
        styles["BodyJust"]
    ))

    story.append(Paragraph("Questão 5 — Se tivesse apenas uma hora, qual seria a primeira ação e por quê?", styles["QTitle"]))
    story.append(Paragraph(
        "<b>Primeira ação:</b> aplicar atualizações de segurança dos pacotes pendentes "
        "(em especial sudo, systemd, libc6, bash, dpkg), após snapshot/backup e janela autorizada, "
        "e registrar o novo baseline.<br/>"
        "<b>Por quê:</b> é a intervenção de maior redução de risco por unidade de tempo com evidência "
        "objetiva já coletada (31 pacotes upgradable). Controles de firewall e política de senha "
        "são prioritários em seguida, mas o fechamento de CVEs conhecidas em bibliotecas/base "
        "do sistema é o ganho mais imediato e mensurável para a auditoria.",
        styles["BodyJust"]
    ))

    story.append(PageBreak())

    # ========== DOC 3: RISCOS ==========
    story.append(Paragraph("DOCUMENTO 3 — Lista Preliminar de Riscos Observados", styles["H1Doc"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
    story.append(risk_table([
        ("Dívida de patches", "Alta",
         "31 pacotes upgradable; inclui sudo, systemd, libc6, bash, dpkg."),
        ("Firewall omitido / não comprovado", "Alta",
         "Sem regras UFW/iptables/nft evidenciadas; sudo bloqueou inspeção completa."),
        ("Política de senha fraca", "Média-Alta",
         "PASS_MAX_DAYS=99999 em /etc/login.defs; contas privilegiadas locais."),
        ("Logging incompleto p/ auditoria", "Média",
         "rsyslog inactive; ausência de trilha auth clássica; sem SIEM evidenciado."),
        ("Sem unattended-upgrades", "Média",
         "Pacote não listado; manutenção automática não evidenciável."),
        ("Plataforma WSL em contexto produtivo", "Média",
         "hostnamectl: Virtualization=wsl; kernel microsoft-standard-WSL2."),
        ("Privilégio sudo sem inventário de regras", "Média",
         "machado∈sudo; /etc/sudoers.d não lido (senha requerida)."),
        ("Gestão de tempo pouco clara", "Baixa-Média",
         "timedatectl: NTP service n/a; chrony/ntp inactive."),
        ("Cron habilitado sem revisão de jobs", "Baixa",
         "cron.service enabled/running; jobs ainda não inventariados."),
    ], styles))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "<i>Nota metodológica:</i> riscos sem evidência direta foram excluídos. Por exemplo, "
        "não se afirma comprometimento ativo: last/who e journal não apresentam indícios claros "
        "de acesso não autorizado.",
        styles["Small"]
    ))

    # ========== DOC 4: PLANO ==========
    story.append(Paragraph("DOCUMENTO 4 — Plano de Investigação para as Próximas Aulas", styles["H1Doc"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
    story.append(Paragraph(
        "1. <b>Governança do ativo:</b> confirmar com a diretoria se o host WSL é o alvo definitivo "
        "de produção ou se haverá provisionamento de VM Debian/Ubuntu Server dedicada.<br/>"
        "2. <b>Baseline de pacotes:</b> dpkg -l completo; comparar com imagem mínima aprovada; "
        "remover pacotes desnecessários.<br/>"
        "3. <b>Identidade e privilégio:</b> auditar /etc/sudoers*; revisar membership de sudo/adm; "
        "avaliar bloqueio de login root e uso de chaves SSH quando SSH for introduzido.<br/>"
        "4. <b>Rede e firewall:</b> definir política default-deny; documentar portas necessárias ao negócio; "
        "implementar UFW ou nftables com evidência de regras.<br/>"
        "5. <b>Patch management:</b> aplicar atualizações; habilitar unattended-upgrades para security; "
        "definir janela e rollback.<br/>"
        "6. <b>Logging e auditoria:</b> padronizar journald+rsyslog (ou equivalente), retenção, "
        "integridade e encaminhamento; habilitar auditd se exigido pela auditoria.<br/>"
        "7. <b>Tempo e integridade:</b> padronizar NTP/chrony; revisar cron/timers; introduzir "
        "checagens de integridade (AIDE/Tripwire) nas aulas de hardening.<br/>"
        "8. <b>Reavaliação:</b> repetir este inventário após cada mudança e gerar diff de baseline.",
        styles["BodyJust"]
    ))

    story.append(PageBreak())

    # ========== RECOMENDAÇÕES (Anexo A) ==========
    story.append(Paragraph("Anexo A — Diagnóstico (síntese ≤ 1 página) e Recomendações Iniciais", styles["H1Doc"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
    story.append(Paragraph("3. Diagnóstico (síntese)", styles["H2Doc"]))
    story.append(Paragraph(
        "O inventário do host MachadoPC (Debian 13) mostra um sistema operacional com suporte "
        "vigente, poucos serviços em execução e baixa exposição de portas no instante da coleta. "
        "Contudo, a análise técnica evidencia gaps clássicos de hardening inicial: patches "
        "pendentes em componentes privilegiados, ausência de prova de firewall, política de "
        "senha ineficaz (PASS_MAX_DAYS=99999), logging local incompleto para auditoria e "
        "incerteza sobre a adequação da plataforma WSL ao escopo produtivo da AmazonTech. "
        "A priorização segue o critério de impacto × evidência: primeiro reduzir CVEs conhecidas "
        "via atualização, depois estabelecer controle de tráfego e identidade, e em seguida "
        "fortalecer telemetria para a auditoria externa das próximas quatro semanas.",
        styles["BodyJust"]
    ))

    story.append(Paragraph("4. Recomendações Iniciais (não executadas neste laboratório)", styles["H2Doc"]))
    story.append(Paragraph(
        "<b>R1 — Aplicar atualizações de segurança e registrar novo baseline.</b><br/>"
        "Justificativa/evidência: 31 pacotes em apt list --upgradable, incluindo sudo/systemd/libc6. "
        "Reduz superfície de exploração conhecida antes de qualquer exposição adicional de serviços.",
        styles["BodyJust"]
    ))
    story.append(Paragraph(
        "<b>R2 — Definir e evidenciar política de firewall (default deny) alinhada às portas do negócio.</b><br/>"
        "Justificativa/evidência: inventário de rede não comprovou regras UFW/iptables/nft ativas. "
        "Sem isso, qualquer serviço futuro (ex.: SSH/HTTP) nascera sem contenção de tráfego.",
        styles["BodyJust"]
    ))
    story.append(Paragraph(
        "<b>R3 — Endurecer identidade: revisar sudoers, ajustar PASS_MAX_DAYS e preparar autenticação remota segura.</b><br/>"
        "Justificativa/evidência: machado∈sudo; PASS_MAX_DAYS=99999; openssh-server ausente hoje "
        "(oportunidade de introduzir SSH já endurecido, com chaves e sem root login, quando necessário).",
        styles["BodyJust"]
    ))

    # ========== FECHAMENTO ==========
    story.append(Paragraph("10. Fechamento do Laboratório", styles["H1Doc"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
    story.append(Paragraph(
        "<b>Quais informações foram mais fáceis de obter?</b> Distribuição, versão, kernel, hostname, "
        "data/hora, lista de usuários/grupos, serviços systemd e interfaces/portas via ss/ip.",
        styles["BodyJust"]
    ))
    story.append(Paragraph(
        "<b>Quais itens exigiram maior investigação?</b> Estado real do firewall e sudoers "
        "(bloqueados por falta de privilégio interativo), correlação dos erros do journal com risco "
        "de segurança, e interpretação da porta 53 no contexto WSL.",
        styles["BodyJust"]
    ))
    story.append(Paragraph(
        "<b>O inventário revelou alguma surpresa?</b> Sim: a percepção da diretoria de que o ambiente "
        "“estaria seguro” contrastou com 31 atualizações pendentes, política de senha permissiva e "
        "falta de evidência de firewall — apesar da baixa exposição imediata de serviços.",
        styles["BodyJust"]
    ))
    story.append(Paragraph(
        "<b>O ambiente estava mais ou menos seguro do que o esperado?</b> "
        "<b>Menos seguro do que o discurso gerencial sugere</b>, embora <b>mais contido</b> do que "
        "um servidor típico com SSH/web expostos. Segurança aparente ≠ prontidão para produção.",
        styles["BodyJust"]
    ))
    story.append(Paragraph(
        "<b>Que tipo de intervenção priorizaríamos se iniciássemos o hardening hoje?</b> "
        "Patch management imediato, seguido de firewall default-deny e endurecimento de contas/"
        "sudo/política de senha, com reforço de logging para a auditoria.",
        styles["BodyJust"]
    ))

    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1.2, color=PRIMARY))
    story.append(Paragraph(
        "<b>Declaração:</b> Nenhuma configuração foi alterada. Este documento registra apenas "
        "observação, inventário e análise preliminar com base em evidências coletadas em 28/07/2026.",
        styles["Small"]
    ))
    story.append(Paragraph(
        "Arquivo de evidências brutas associado: evidencias/inventory_raw.txt (saídas de terminal).",
        styles["Small"]
    ))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
