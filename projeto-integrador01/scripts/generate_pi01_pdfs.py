#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Projeto Integrador 01: Ordem de Servico + Projeto Tecnico (Hardening DB-01 PostgreSQL)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    PageBreak, HRFlowable, Image as RLImage, KeepTogether, ListFlowable, ListItem
)

BASE = Path(r"d:\MMB\workspace\hardening\projeto-integrador01")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "PI01_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_PROJ = BASE / "entregaveis" / "PI01_Projeto_Tecnico_Hardening_DB01_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\PI01_Ordem_de_Servico_PREENCHIDO.pdf")
DL_PROJ = Path(r"c:\Users\marge\Downloads\PI01_Projeto_Tecnico_Hardening_DB01_PREENCHIDO.pdf")

TEAM = "Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato"
TEAM_SHORT = "Josias, Keven, Margefson, Nattan"
DATE = "06/08/2026"

PRIMARY = HexColor("#1a365d")
ACCENT = HexColor("#2c5282")
LIGHT = HexColor("#edf2f7")
OK = HexColor("#276749")
WARN = HexColor("#c05621")
BORDER = HexColor("#cbd5e0")

SHOT_META = [
    ("01_cenario_db01", "Anexo A - Cenario DB-01 (PostgreSQL)"),
    ("02_baseline_web01", "Anexo B - Baseline corporativa derivada do WEB-01"),
    ("03_matriz_decisoes", "Anexo C - Matriz resumida de decisoes"),
]


def font(size=14, bold=False):
    cands = [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf"]
    if bold:
        cands = [r"C:\Windows\Fonts\consolab.ttf"] + cands
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def write_evidence_files():
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    (SHOT_DIR / "01_cenario_db01.txt").write_text(
        "\n".join([
            "AmazonTech | Projeto Integrador 01 | Consultoria Hardening",
            "Cenario selecionado: DB-01 (Servidor de Banco de Dados PostgreSQL)",
            "",
            "Finalidade: persistencia de dados corporativos (ERP/apps internas)",
            "SO alvo: Debian 13 / Ubuntu 24.04 LTS (linha Debian)",
            "Servico principal: postgresql (porta 5432/tcp - apenas rede interna)",
            "Admin remoto: sshd (22/tcp) restrito a bastion/VPN",
            "Usuarios: DBAs (grupo dba), app runtime (nologin), auditores (ro)",
            "",
            "Requisitos CIA:",
            "  Confidencialidade: ALTA (dados sensiveis de negocio)",
            "  Integridade: ALTA (transacoes e consistencia)",
            "  Disponibilidade: ALTA (RTO/RPO definidos pela operacao)",
            "",
            "Diferenca vs WEB-01: foco em dados em repouso/transito DB,",
            "superficie de rede menor (sem HTTP publico), backup/PITR critico.",
        ]),
        encoding="utf-8",
    )
    (SHOT_DIR / "02_baseline_web01.txt").write_text(
        "\n".join([
            "Baseline corporativa validada no WEB-01 (Labs 01-04B) - reuso no DB-01:",
            "",
            "[Lab01] Inventario antes de mudar | evidencia de estado",
            "[Lab02] Identidades/grupos | sudo restrito | 750/770 | ACL excepcional",
            "[Lab03] Menor funcionalidade | SSH harden | UFW deny | Fail2Ban | AIDE | Lynis HI=69",
            "[Lab04A] MAC SELinux Enforcing | labels/restorecon/semanage",
            "[Lab04B] apt security | debsecan | Lynis periodico | AIDE/debsums | plano continuo",
            "",
            "Principios permanentes AmazonTech:",
            "  menor privilegio | menor funcionalidade | menor comunicacao",
            "  defesa em profundidade | evidencia antes de opiniao | manutencao continua",
        ]),
        encoding="utf-8",
    )
    (SHOT_DIR / "03_matriz_decisoes.txt").write_text(
        "\n".join([
            "Matriz resumida (detalhe no Apendice A do Projeto Tecnico):",
            "",
            "Decisao                         | Conceito              | Aula",
            "------------------------------- | --------------------- | -----",
            "sudo + grupos dba/app/audit     | menor privilegio      | 2",
            "desabilitar servicos nao-DB     | menor funcionalidade  | 3",
            "UFW: 22 + 5432 interna only     | menor comunicacao     | 3",
            "SELinux + dominio postgresql    | MAC                   | 4A",
            "apt security + debsecan         | vulnerabilidades      | 4B",
            "Lynis + AIDE + backup PITR      | auditoria/integridade | 4B",
            "Fail2Ban sshd (nao 5432 brute)  | defesa em profundidade | 3",
        ]),
        encoding="utf-8",
    )


def render_terminal(text, title, out_path, max_lines=28):
    lines = text.replace("\t", "    ").splitlines()
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + ["..."]
    f, ft = font(13), font(12, True)
    line_h, pad_x, pad_y, title_h = 18, 16, 14, 34
    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    max_w = max((d.textbbox((0, 0), ln, font=f)[2] for ln in lines), default=700)
    max_w = max(max_w, d.textbbox((0, 0), title, font=ft)[2])
    w = min(max(max_w + pad_x * 2, 780), 1100)
    h = title_h + pad_y * 2 + max(len(lines), 1) * line_h + 10
    img = Image.new("RGB", (w, h), "#0d1117")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, title_h], fill="#21262d")
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        x = 14 + i * 16
        draw.ellipse([x, 11, x + 10, 21], fill=c)
    draw.text((70, 9), title, font=ft, fill="#c9d1d9")
    y = title_h + pad_y
    for ln in lines:
        color = "#c9d1d9"
        if ln.startswith("[") or "ALTA" in ln or "SELinux" in ln:
            color = "#79c0ff"
        elif ln.startswith("Decisao") or "----" in ln:
            color = "#8b949e"
        draw.text((pad_x, y), ln[:170], font=f, fill=color)
        y += line_h
    draw.rectangle([0, 0, w - 1, h - 1], outline="#30363d")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def generate_shots():
    write_evidence_files()
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}
    for key, title in SHOT_META:
        txt = (SHOT_DIR / f"{key}.txt").read_text(encoding="utf-8")
        out = IMG_DIR / f"{key}.png"
        render_terminal(txt, title, out)
        paths[key] = out
        print("shot:", out.name)
    return paths


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=13,
                         textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6, leading=16))
    s.add(ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=9.5,
                         textColor=ACCENT, alignment=TA_CENTER, spaceAfter=3, leading=12))
    s.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=11,
                         textColor=PRIMARY, spaceBefore=8, spaceAfter=4, leading=13))
    s.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=9.5,
                         textColor=ACCENT, spaceBefore=6, spaceAfter=3, leading=12))
    s.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=8.5,
                         alignment=TA_JUSTIFY, spaceAfter=4, leading=11))
    s.add(ParagraphStyle("Cap", fontName="Helvetica-Oblique", fontSize=7.5,
                         textColor=HexColor("#4a5568"), alignment=TA_CENTER,
                         spaceBefore=2, spaceAfter=5, leading=9))
    s.add(ParagraphStyle("Meta", fontName="Helvetica", fontSize=8.5,
                         textColor=HexColor("#4a5568"), alignment=TA_CENTER, spaceAfter=2))
    s.add(ParagraphStyle("Small", fontName="Helvetica", fontSize=7.5,
                         textColor=HexColor("#4a5568"), alignment=TA_JUSTIFY, spaceAfter=2, leading=9.5))
    s.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=7, leading=9))
    s.add(ParagraphStyle("Head", fontName="Helvetica-Bold", fontSize=7, textColor=white, leading=9))
    s.add(ParagraphStyle("TOC", fontName="Helvetica", fontSize=9, leading=12, spaceAfter=2))
    return s


def footer(title):
    def _f(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(PRIMARY)
        canvas.setLineWidth(1)
        canvas.line(1.4*cm, A4[1]-1.15*cm, A4[0]-1.4*cm, A4[1]-1.15*cm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(ACCENT)
        canvas.drawString(1.4*cm, A4[1]-1.0*cm, title)
        canvas.drawRightString(A4[0]-1.4*cm, A4[1]-1.0*cm, "AmazonTech DB-01")
        canvas.line(1.4*cm, 1.2*cm, A4[0]-1.4*cm, 1.2*cm)
        canvas.drawCentredString(A4[0]/2, 0.75*cm,
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | PI-01")
        canvas.restoreState()
    return _f


def kv(rows, st, c1=4.5*cm, c2=12.2*cm):
    data = [[Paragraph(f"<b>{k}</b>", st["Cell"]), Paragraph(str(v), st["Cell"])] for k, v in rows]
    t = Table(data, colWidths=[c1, c2])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def grid(headers, rows, st, widths, head_color=PRIMARY):
    data = [[Paragraph(h, st["Head"]) for h in headers]]
    for r in rows:
        data.append([Paragraph(str(c), st["Cell"]) for c in r])
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), head_color),
        ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
    ]))
    return t


def shot(paths, key, st, width=16.5*cm):
    p = paths[key]
    im = Image.open(p)
    w, h = im.size
    tw = width
    th = tw * (h / w)
    if th > 8.0*cm:
        th = 8.0*cm
        tw = th * (w / h)
    return KeepTogether([
        RLImage(str(p), width=tw, height=th),
        Paragraph(f"<i>Figura - {dict(SHOT_META)[key]}</i>", st["Cap"]),
    ])


def hr():
    return HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=5)


def build_os(paths):
    st = styles()
    OUT_OS.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT_OS), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="PI01 - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("PROJETO INTEGRADOR - ORDEM DE SERVICO", st["CoverSub"]))
    story.append(Paragraph("Planejamento de Politica Corporativa de Hardening Linux", st["CoverTitle"]))
    story.append(Paragraph("Cenario: DB-01 — Servidor de Banco de Dados PostgreSQL", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe (Consultoria):</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(f"Status: CONCLUIDA | Data: {DATE}", st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Diretoria de Tecnologia da Informacao"),
        ("Area solicitante", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Tipo", "Projeto Integrador / Consultoria Tecnica"),
        ("Produto esperado", "Projeto de Politica Corporativa de Hardening Linux"),
        ("Ambiente escolhido", "<b>DB-01 — PostgreSQL (Banco de Dados)</b>"),
        ("Equipe", TEAM),
        ("Data", DATE),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Contexto e Decisao do Cenario", st["H1"]))
    story.append(Paragraph(
        "A AmazonTech validou no WEB-01 (Labs 01-04B) um padrao corporativo de Hardening. "
        "A Diretoria solicitou agora politicas adaptaveis a outros tipos de servidor. "
        "A consultoria selecionou o <b>servidor de banco de dados PostgreSQL (DB-01)</b> por: "
        "(1) criticidade de confidencialidade/integridade; (2) perfil de risco distinto do WEB-01 "
        "(sem exposicao HTTP publica; foco em 5432 interno e dados); (3) necessidade clara de "
        "backup/PITR e segregacao DBA/app; (4) reaproveitamento justificado da baseline WEB-01 "
        "com adaptacoes tecnicas.",
        st["Body"]))
    story.append(shot(paths, "01_cenario_db01", st))

    story.append(Paragraph("3. Entregaveis da OS", st["H1"]))
    story.append(grid(
        ["Entregavel", "Status"],
        [
            ["Caracterizacao do ambiente DB-01", "SIM"],
            ["Levantamento de ativos e analise de riscos", "SIM"],
            ["Politica integrada de Hardening (12 controles)", "SIM"],
            ["Selecao e justificativa de ferramentas", "SIM"],
            ["Plano de implantacao + manutencao continua", "SIM"],
            ["Matriz de justificativa (Apendice A) + checklist", "SIM"],
            ["Projeto Tecnico PDF para a Diretoria", "SIM"],
        ],
        st, [13.5*cm, 3.2*cm], OK
    ))

    story.append(Paragraph("4. Conformidade com Objetivos da OS", st["H1"]))
    story.append(grid(
        ["Objetivo especifico", "Atendido?"],
        [
            ["Caracterizar o ambiente selecionado", "SIM"],
            ["Identificar ativos envolvidos", "SIM"],
            ["Analisar riscos do servidor", "SIM"],
            ["Definir politica integrada de Hardening", "SIM"],
            ["Selecionar mecanismos compativeis", "SIM"],
            ["Justificar tecnicamente cada mecanismo", "SIM"],
            ["Propor manutencao continua", "SIM"],
            ["Documentacao em padrao de consultoria", "SIM"],
        ],
        st, [13.5*cm, 3.2*cm], OK
    ))
    story.append(kv([
        ("Documento tecnico", "PI01_Projeto_Tecnico_Hardening_DB01_PREENCHIDO.pdf"),
        ("Referencia baseline", "Labs WEB-01 (lab01..lab04b)"),
        ("Parecer", "RECOMENDADA a implantacao da politica proposta"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("PI01 - Ordem de Servico"),
              onLaterPages=footer("PI01 - Ordem de Servico"))
    print("OS OK")


def build_project(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_PROJ), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="PI01 - Projeto Tecnico Hardening DB-01", author=TEAM)
    story = []

    # Cover
    story.append(Paragraph("AMAZONTECH — Diretoria de Tecnologia da Informacao", st["CoverSub"]))
    story.append(Paragraph("PROJETO TECNICO", st["CoverTitle"]))
    story.append(Paragraph(
        "Proposta de Politica de Hardening para Ambiente Linux Corporativo",
        st["CoverSub"]))
    story.append(Paragraph("<b>Ambiente:</b> DB-01 — Servidor de Banco de Dados PostgreSQL", st["Meta"]))
    story.append(Paragraph(f"<b>Equipe consultora:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Disciplina: Hardening Linux | Data: {DATE}",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("Sumario", st["H1"]))
    for line in [
        "1. Introducao",
        "2. Caracterizacao do Ambiente",
        "3. Levantamento dos Ativos",
        "4. Analise dos Riscos",
        "5. Politica Proposta de Hardening",
        "6. Ferramentas Selecionadas",
        "7. Plano de Implantacao",
        "8. Plano Permanente de Manutencao",
        "9. Beneficios Esperados",
        "10. Limitacoes do Projeto",
        "11. Parecer Tecnico",
        "12. Conclusoes",
        "Referencias | Anexos | Apendice A (Matriz) | Checklist",
    ]:
        story.append(Paragraph(line, st["TOC"]))
    story.append(PageBreak())

    # 1
    story.append(Paragraph("1. Introducao", st["H1"]))
    story.append(Paragraph(
        "Este projeto e o produto da consultoria contratada pela AmazonTech para elaborar uma "
        "politica corporativa de Hardening Linux adaptavel a ambientes distintos do WEB-01. "
        "Ao longo da disciplina, a equipe implantou e validou no WEB-01 controles de identidade, "
        "reducao de superficie, MAC (SELinux) e manutencao continua. A Diretoria reconhece que "
        "cada tipo de servidor exige adaptacoes. A proposta a seguir define Hardening para o "
        "<b>DB-01 (PostgreSQL)</b>, reutilizando principios validados e justificando desvios "
        "em funcao da finalidade do banco de dados (dados sensiveis, disponibilidade transacional, "
        "acesso restrito a rede interna).",
        st["Body"]))
    story.append(Paragraph(
        "Objetivo geral: entregar politica tecnicamente consistente, operacionalmente viavel e "
        "alinhada as boas praticas da disciplina, servindo de referencia para futuras implantacoes.",
        st["Body"]))

    # 2
    story.append(Paragraph("2. Caracterizacao do Ambiente", st["H1"]))
    story.append(kv([
        ("Tipo de servidor", "Banco de dados (PostgreSQL)"),
        ("Hostname proposto", "DB-01"),
        ("Finalidade", "Persistencia de dados de aplicacoes corporativas AmazonTech"),
        ("Principais servicos", "postgresql, sshd, rsyslog/journald, cron, UFW, Fail2Ban, AIDE"),
        ("Usuarios atendidos", "Aplicacoes (contas de servico), DBAs, auditores (leitura)"),
        ("Disponibilidade", "Alta — janelas controladas; RTO/RPO definidos com operacao"),
        ("Confidencialidade", "Alta — dados de negocio e eventualmente PII"),
        ("Integridade", "Alta — consistencia transacional e trilha de mudancas"),
        ("SO recomendado", "Debian 13 ou Ubuntu 24.04 LTS (padrao corporativo pos-WEB-01)"),
    ], st))
    story.append(shot(paths, "01_cenario_db01", st))

    # 3
    story.append(Paragraph("3. Levantamento dos Ativos", st["H1"]))
    story.append(grid(
        ["Ativo", "Importancia", "Justificativa"],
        [
            ["Dados PostgreSQL (clusters/DBs)", "Critica", "Nucleo do negocio; impacto direto se vazados/corrompidos"],
            ["Credenciais DB / roles", "Critica", "Comprometimento implica acesso amplo aos dados"],
            ["SO e pacotes base", "Alta", "Base de confianca; CVEs em libs afetam o servico"],
            ["Backups / WAL / PITR", "Critica", "Recuperacao ante ransomware, erro humano ou desastre"],
            ["Canal SSH admin", "Alta", "Via privilegiada de administracao"],
            ["Logs (PostgreSQL + SO)", "Alta", "Deteccao, forense e conformidade"],
            ["Politicas MAC/firewall", "Alta", "Contecao e menor comunicacao"],
        ],
        st, [5.0*cm, 2.5*cm, 9.2*cm]
    ))

    # 4
    story.append(Paragraph("4. Analise dos Riscos", st["H1"]))
    story.append(grid(
        ["Risco", "Impacto", "Prob.", "Estrategia proposta"],
        [
            ["Exposicao 5432 a Internet", "Critico", "Media", "UFW: 5432 so rede app/VPN; sem bind publico"],
            ["Credencial DBA fraca/compartilhada", "Alto", "Media", "Contas nominais; sudo; senha/pam; MFA no bastion"],
            ["SQL injection via app", "Alto", "Media", "Role least-privilege no DB; app user != superuser"],
            ["Ransomware / wipe de dados", "Critico", "Baixa-Media", "Backup offline/offsite + PITR + teste restore"],
            ["CVE em PostgreSQL/libs", "Alto", "Media", "apt security + debsecan; janela de patch"],
            ["Alteracao indevida de configs", "Alto", "Media", "AIDE + MAC + change control"],
            ["Brute-force SSH", "Medio", "Media", "SSH harden + Fail2Ban + AllowUsers"],
            ["Privilégio excessivo app/OS", "Alto", "Media", "Grupos, sudo, nologin em contas servico"],
        ],
        st, [4.2*cm, 2.0*cm, 2.0*cm, 8.5*cm], WARN
    ))
    story.append(PageBreak())

    # 5 Politica
    story.append(Paragraph("5. Politica Proposta de Hardening", st["H1"]))
    story.append(Paragraph(
        "A politica integra os controles validados no WEB-01, adaptados ao perfil de banco de dados. "
        "Cada subsecao traz a decisao e a justificativa tecnica.",
        st["Body"]))

    story.append(Paragraph("5.1 Controle de Identidades", st["H2"]))
    story.append(Paragraph(
        "<b>Decisao:</b> grupos <i>dba</i> (admin DB/OS limitado), <i>dbapp</i> (donos de processos app "
        "no host, se houver), <i>dbaudit</i> (leitura de logs); contas nominais; conta de servico "
        "PostgreSQL com shell nologin; proibir usuarios genericos compartilhados.<br/>"
        "<b>Justificativa:</b> menor privilegio e rastreabilidade (Lab 02). Em DB, segregacao DBA vs "
        "app reduz blast radius de comprometimento da aplicacao.",
        st["Body"]))

    story.append(Paragraph("5.2 Controle de Privilegios", st["H2"]))
    story.append(Paragraph(
        "<b>Decisao:</b> sudo apenas para grupo dba/admin com logging; regras especificas "
        "(systemctl status postgresql, reload, backup) em vez de ALL indiscriminado; ACL apenas "
        "excepcional e temporaria em diretorios de evidencias/backup, com remocao apos uso.<br/>"
        "<b>Justificativa:</b> Lab 02 demonstrou risco de sudo amplo e valor de ACL pontual.",
        st["Body"]))

    story.append(Paragraph("5.3 Servicos do Sistema", st["H2"]))
    story.append(Paragraph(
        "<b>Manter:</b> postgresql, sshd, rsyslog/journald, cron, UFW, Fail2Ban, chrony/NTP, AIDE.<br/>"
        "<b>Desabilitar:</b> MTA local nao necessario (exim), servicos de desktop, compartilhamento "
        "arquivo generico, containers nao usados, qualquer listener HTTP/HTTPS neste host.<br/>"
        "<b>Justificativa:</b> menor funcionalidade (Lab 03); DB-01 nao e web server.",
        st["Body"]))

    story.append(Paragraph("5.4 Configuracao do SSH", st["H2"]))
    story.append(Paragraph(
        "<b>Politica:</b> PermitRootLogin no; PubkeyAuthentication yes; PasswordAuthentication "
        "preferencialmente no em producao (lab pode manter senha); X11Forwarding no; MaxAuthTries 3; "
        "AllowUsers/AllowGroups restrito a admins; Banner legal.<br/>"
        "<b>Justificativa:</b> canal admin e alvo primario; mesmo padrao WEB-01 (Lab 03).",
        st["Body"]))

    story.append(Paragraph("5.5 Firewall", st["H2"]))
    story.append(Paragraph(
        "<b>Politica:</b> UFW default deny incoming / allow outgoing; allow 22/tcp somente de "
        "bastion/VPN; allow 5432/tcp somente de sub-rede das aplicacoes (WEB-01/app-tier); "
        "negar 5432 de qualquer outra origem.<br/>"
        "<b>Justificativa:</b> menor comunicacao; DB nunca deve ser alcancavel da Internet.",
        st["Body"]))

    story.append(Paragraph("5.6 Mandatory Access Control", st["H2"]))
    story.append(Paragraph(
        "<b>Escolha:</b> <b>SELinux</b> (Enforcing), alinhado ao padrao validado no WEB-01 "
        "(Lab 04A) e ao LSM disponivel no padrao corporativo da equipe. Politica targeted/default "
        "com dominio adequado ao PostgreSQL; restorecon apos restore de dados; semanage fcontext "
        "para paths de data/WAL/backup.<br/>"
        "<b>AppArmor:</b> alternativa valida em Ubuntu puro; nao e a escolha primaria desta "
        "proposta porque a baseline AmazonTech ja operacionalizou SELinux no programa WEB-01.<br/>"
        "<b>Justificativa:</b> MAC limita processo postgres mesmo apos falha de DAC/app.",
        st["Body"]))

    story.append(Paragraph("5.7 Atualizacoes", st["H2"]))
    story.append(Paragraph(
        "<b>Estrategia:</b> apt update diario; security upgrades em janela semanal (criticos 24-72h); "
        "teste em homolog DB antes de producao; needrestart/avaliacao de restart do PostgreSQL; "
        "registro de evidencias (Lab 04B).<br/>"
        "<b>Criterios:</b> priorizar CVEs que afetam postgresql, openssl, libc, kernel.",
        st["Body"]))

    story.append(Paragraph("5.8 Gerenciamento de Vulnerabilidades", st["H2"]))
    story.append(Paragraph(
        "<b>Ferramentas:</b> debsecan (Debian/Ubuntu); consulta a security.debian.org / USN; "
        "opcional scanner de vulnerabilidades de imagem/host da organizacao.<br/>"
        "<b>Procedimento:</b> triagem semanal; ticket com CVE, pacote, severidade, prazo; "
        "nem todo CVE exige patch imediato — avaliar explorabilidade e exposicao.",
        st["Body"]))

    story.append(Paragraph("5.9 Auditoria", st["H2"]))
    story.append(Paragraph(
        "<b>Ferramentas:</b> Lynis (mensal + pos-mudanca); logging sudo; logs PostgreSQL "
        "(conexoes, DDL sensivel); opcional auditd para paths de data.<br/>"
        "<b>Meta:</b> acompanhar Hardening Index e warnings; nao tratar HI como nota absoluta.",
        st["Body"]))

    story.append(Paragraph("5.10 Integridade", st["H2"]))
    story.append(Paragraph(
        "<b>Estrategia:</b> AIDE com baseline apos hardening inicial; check semanal e apos patches; "
        "debsums mensal; investigar diffs antes de atualizar DB do AIDE (Lab 04B).<br/>"
        "<b>Justificativa:</b> detecta alteracoes em binarios/configs criticos do SO e do DB.",
        st["Body"]))

    story.append(Paragraph("5.11 Backup e Recuperacao", st["H2"]))
    story.append(Paragraph(
        "<b>Estrategia:</b> backups periodicos (pg_basebackup/pg_dump conforme RPO) + arquivamento "
        "WAL (PITR); copia offsite; teste de restore trimestral; criptografia em transito/repouso "
        "dos backups; acesso restrito ao storage de backup.<br/>"
        "<b>Justificativa:</b> ativo critico do DB-01; Hardening sem recuperacao e incompleto "
        "para ransomware/erro humano. (Controle adicional vs WEB-01 puro.)",
        st["Body"]))

    story.append(Paragraph("5.12 Documentacao", st["H2"]))
    story.append(Paragraph(
        "<b>Documentos:</b> runbook de implantacao; inventario; matriz de portas; politica sudo; "
        "procedimentos de patch/backup/restore; registro de auditorias Lynis/AIDE; este Projeto "
        "Tecnico como referencia corporativa.<br/>"
        "<b>Justificativa:</b> continuidade operacional e transferencia entre equipes.",
        st["Body"]))
    story.append(PageBreak())

    # 6
    story.append(Paragraph("6. Ferramentas Selecionadas", st["H1"]))
    story.append(Paragraph(
        "Apenas ferramentas necessarias ao DB-01 (nao e obrigatorio usar todas da disciplina).",
        st["Body"]))
    story.append(grid(
        ["Ferramenta", "Finalidade", "Justificativa"],
        [
            ["apt / security pocket", "Atualizacoes", "Correcao de CVEs conhecidos (Lab 04B)"],
            ["debsecan", "Vulnerabilidades", "Visao de CVEs por pacote no Debian"],
            ["UFW", "Firewall host", "Menor comunicacao 22/5432"],
            ["Fail2Ban (sshd)", "Anti brute-force", "Protege admin; 5432 nao e o foco do jail"],
            ["OpenSSH harden", "Acesso admin", "Canal privilegiado"],
            ["SELinux", "MAC", "Contecao de processos (Lab 04A)"],
            ["AIDE", "Integridade", "Detecta mudancas indevidas"],
            ["debsums", "Integridade pacotes", "Complementa AIDE"],
            ["Lynis", "Auditoria config", "Indicador continuo de hardening"],
            ["rsyslog/journald", "Logs", "Trilha operacional/forense"],
            ["pg_basebackup/WAL", "Backup/PITR", "Recuperacao especifica de DB"],
        ],
        st, [3.8*cm, 4.2*cm, 8.7*cm]
    ))
    story.append(Paragraph(
        "<b>Descartado neste host:</b> stack HTTP/Nginx como servico local; AppArmor como MAC "
        "primario (SELinux padronizado); scanners web (pertencem ao WEB-01).",
        st["Body"]))

    # 7
    story.append(Paragraph("7. Plano de Implantacao", st["H1"]))
    story.append(grid(
        ["Etapa", "Atividade", "Objetivo"],
        [
            ["1", "Inventario e baseline (Lynis/AIDE inicial)", "Conhecer estado antes de mudar"],
            ["2", "Identidades, grupos, sudo, nologin servicos", "Menor privilegio"],
            ["3", "Desabilitar servicos nao essenciais", "Menor funcionalidade"],
            ["4", "Hardening SSH + UFW + Fail2Ban", "Proteger admin e rede"],
            ["5", "Instalar/configurar PostgreSQL seguro + roles", "Servico alinhado a politica"],
            ["6", "SELinux Enforcing + fcontext data/WAL", "MAC operacional"],
            ["7", "Backup/PITR + teste de restore", "Recuperabilidade"],
            ["8", "Auditoria final Lynis + evidencias + Go-Live", "Aceite operacional"],
        ],
        st, [1.5*cm, 8.5*cm, 6.7*cm]
    ))

    # 8
    story.append(Paragraph("8. Plano Permanente de Manutencao", st["H1"]))
    story.append(Paragraph(
        "<b>Atualizacoes:</b> diarias (apt update); security semanal; criticos sob demanda.<br/>"
        "<b>Vulnerabilidades:</b> debsecan semanal; DSA/USN; tickets priorizados.<br/>"
        "<b>Auditorias:</b> Lynis mensal; revisao de suggestions; acompanhamento do HI.<br/>"
        "<b>Monitoramento:</b> logs Postgres/SSH/UFW; alertas de disco/conexoes; Fail2Ban.<br/>"
        "<b>Integridade:</b> AIDE semanal; debsums mensal; investigar antes de update DB.<br/>"
        "<b>Evidencias:</b> data, responsavel, ferramentas, achados, pendencias.<br/>"
        "<b>Revisao da politica:</b> semestral ou apos incidente/mudanca de arquitetura.",
        st["Body"]))
    story.append(grid(
        ["Frequencia", "Atividades DB-01"],
        [
            ["Diariamente", "apt update; checar backups/WAL; alertas auth/firewall"],
            ["Semanalmente", "security upgrade; debsecan; AIDE check; revisar fails SSH"],
            ["Mensalmente", "Lynis; debsums; teste amostral de restore; revisar roles DB"],
            ["Trimestralmente", "restore completo em homolog; revisao de capacidade/RPO"],
        ],
        st, [3.5*cm, 13.2*cm]
    ))
    story.append(PageBreak())

    # 9
    story.append(Paragraph("9. Beneficios Esperados", st["H1"]))
    story.append(Paragraph(
        "<b>Seguranca:</b> menor superficie, MAC, patch continuo e segregacao de papeis.<br/>"
        "<b>Disponibilidade:</b> janelas controladas, backup/PITR e menor risco de wipe.<br/>"
        "<b>Administracao:</b> padrao alinhado ao WEB-01 reduz curva de aprendizado.<br/>"
        "<b>Conformidade:</b> evidencias periodicas sustentam auditorias internas.<br/>"
        "<b>Reducao de riscos:</b> 5432 nao publico + least privilege mitiga incidentes tipicos de DB.",
        st["Body"]))

    # 10
    story.append(Paragraph("10. Limitacoes do Projeto", st["H1"]))
    story.append(Paragraph(
        "Esta e uma proposta de politica/consultoria: nao substitui implementacao fisica do DB-01 "
        "neste repositorio. Nao cobre WAF/aplicacao (responsabilidade do tier web). Nao detalha "
        "HA multi-AZ completo (pode ser fase 2). Ferramentas comerciais de DLP/SIEM ficam fora "
        "do escopo academico, embora compativeis. O Hardening Index Lynis e indicador, nao "
        "certificacao. Adesao depende de change control e capacitacao da operacao AmazonTech.",
        st["Body"]))

    # 11
    story.append(Paragraph("11. Parecer Tecnico", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Cliente", "AmazonTech — Diretoria de TI"),
        ("Objeto", "Politica de Hardening DB-01 (PostgreSQL)"),
        ("Consultoria", TEAM),
        ("Data", DATE),
        ("Recomendacao", "<b>IMPLANTAR</b> a politica proposta"),
    ], st))
    story.append(Paragraph(
        "Na condicao de consultores, avaliamos que a politica e <b>adequada ao ambiente de banco "
        "de dados</b>: reutiliza a baseline corporativa do WEB-01 (identidades, SSH, firewall, "
        "MAC, patch, auditoria, integridade) e introduz controles especificos indispensaveis ao "
        "DB (restricao de 5432, roles least-privilege, backup/PITR, foco em dados).<br/><br/>"
        "<b>Beneficios:</b> reducao material de risco de exposicao e privilegio excessivo; "
        "recuperabilidade; padronizacao operacional.<br/>"
        "<b>Limitacoes:</b> exige disciplina de janelas, testes de restore e gestao de CVEs; "
        "HA geografico e controles de aplicacao sao complementares.<br/>"
        "<b>Recomendacoes de implantacao:</b> seguir o plano em 8 etapas; homologar patches; "
        "validar SELinux com carga Postgres; executar restore teste antes do Go-Live.<br/>"
        "<b>Manutencao futura:</b> adotar o ciclo diario/semanal/mensal da Secao 8; revisar "
        "politica semestralmente; integrar evidencias ao SGSI corporativo.<br/><br/>"
        "<b>Parecer final:</b> [X] <b>RECOMENDADA A IMPLANTACAO</b> da Politica de Hardening "
        f"para o DB-01.<br/><b>Responsaveis:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    # 12
    story.append(Paragraph("12. Conclusoes", st["H1"]))
    story.append(Paragraph(
        "O Projeto Integrador consolidou a passagem de execucao guiada (labs) para decisao "
        "tecnica autonoma. A escolha do DB-01 demonstrou que Hardening e contextual: os mesmos "
        "principios mudam de enfase conforme o ativo. Dificuldade principal: balancear "
        "seguranca e disponibilidade em patches/restarts de banco. Decisao mais relevante: "
        "manter SELinux + firewall estrito em 5432 + backup/PITR como pilares. Politicas "
        "adaptadas por tipo de servidor sao essenciais para a AmazonTech escalar com seguranca.",
        st["Body"]))

    story.append(Paragraph("Referencias", st["H1"]))
    story.append(Paragraph(
        "1. Documentacao dos Labs AmazonTech WEB-01 (lab01–lab04b) deste repositorio.<br/>"
        "2. Debian Security — https://www.debian.org/security/<br/>"
        "3. PostgreSQL Documentation — Security / Backup and Restore.<br/>"
        "4. CIS Benchmarks (Linux / PostgreSQL) — referencia de boas praticas.<br/>"
        "5. Lynis / AIDE / SELinux / UFW man pages e guias oficiais.<br/>"
        "6. Materiais da disciplina Windows e Linux Hardening (Aulas 1–4).",
        st["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("Anexos", st["H1"]))
    story.append(shot(paths, "02_baseline_web01", st))
    story.append(shot(paths, "03_matriz_decisoes", st))

    story.append(Paragraph("Apendice A — Matriz de Justificativa das Decisoes Tecnicas", st["H1"]))
    story.append(grid(
        ["Decisao adotada", "Justificativa tecnica", "Aula"],
        [
            ["Grupos dba/dbapp/dbaudit + sudo restrito", "Menor privilegio e segregacao de funcoes", "2"],
            ["Conta servico nologin", "Eliminar login interativo desnecessario", "2"],
            ["Desabilitar MTA/HTTP no DB-01", "Menor funcionalidade / superficie", "3"],
            ["SSH PermitRootLogin no + AllowUsers", "Endurecer canal administrativo", "3"],
            ["UFW deny; 22 bastion; 5432 so app-tier", "Menor comunicacao", "3"],
            ["Fail2Ban jail sshd", "Resposta a brute-force", "3"],
            ["SELinux Enforcing + fcontext DB", "Mandatory Access Control", "4A"],
            ["apt security + debsecan", "Gestao de vulnerabilidades", "4B"],
            ["Lynis periodico", "Auditoria continua de configuracao", "4B"],
            ["AIDE + debsums", "Integridade de arquivos/pacotes", "4B"],
            ["Backup/PITR + teste restore", "Disponibilidade e recuperacao (especifico DB)", "4B+PI"],
            ["Plano diario/semanal/mensal", "Manutencao continua do Hardening", "4B"],
        ],
        st, [6.0*cm, 7.5*cm, 3.2*cm]
    ))

    story.append(Paragraph("Checklist Operacional de Hardening — DB-01", st["H2"]))
    story.append(grid(
        ["Atividade", "Status proposta", "Evidencia / referencia"],
        [
            ["Inventario e baseline", "Planejado", "Etapa 1 implantacao"],
            ["Identidades e privilegios", "Definido", "Secoes 5.1–5.2"],
            ["Servicos / SSH / Firewall", "Definido", "Secoes 5.3–5.5"],
            ["MAC SELinux", "Definido", "Secao 5.6"],
            ["Patch + vulnerabilidades", "Definido", "Secoes 5.7–5.8"],
            ["Auditoria Lynis", "Definido", "Secao 5.9"],
            ["Integridade AIDE/debsums", "Definido", "Secao 5.10"],
            ["Backup/PITR testado", "Definido", "Secao 5.11"],
            ["Documentacao e evidencias", "Definido", "Secao 5.12 / 8"],
            ["Plano de manutencao atualizado", "SIM", "Secao 8"],
        ],
        st, [5.5*cm, 3.2*cm, 8.0*cm], OK
    ))
    story.append(Paragraph(
        f"Documento gerado em {DATE} | Consultoria: {TEAM} | AmazonTech DB-01",
        st["Small"]))

    doc.build(story, onFirstPage=footer("PI01 - Projeto Tecnico Hardening DB-01"),
              onLaterPages=footer("PI01 - Projeto Tecnico Hardening DB-01"))
    print("PROJ OK")


if __name__ == "__main__":
    paths = generate_shots()
    build_os(paths)
    build_project(paths)
    shutil.copy2(OUT_OS, DL_OS)
    shutil.copy2(OUT_PROJ, DL_PROJ)
    print("Downloads:")
    print(DL_OS)
    print(DL_PROJ)
