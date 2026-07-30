#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 01 PDF com screenshots de terminal."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    PageBreak, HRFlowable, Image as RLImage, KeepTogether
)

BASE = Path(r"d:\MMB\workspace\hardening\lab01")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT = BASE / "entregaveis" / "Lab01_Inventario_Inicial_Seguranca_PREENCHIDO.pdf"
DL = Path(r"c:\Users\marge\Downloads\Lab01_Inventario_Inicial_Seguranca_PREENCHIDO.pdf")

PRIMARY = HexColor("#1a365d")
ACCENT = HexColor("#2c5282")
LIGHT = HexColor("#edf2f7")
OK = HexColor("#276749")
WARN = HexColor("#c05621")
BORDER = HexColor("#cbd5e0")

SHOT_META = [
    ("01_sistema", "Evidencia 1 - Identificacao do sistema (SO/Kernel/hostname)"),
    ("02_usuarios", "Evidencia 2 - Usuarios cadastrados"),
    ("03_grupos", "Evidencia 3 - Grupos administrativos e corporativos"),
    ("04_servicos", "Evidencia 4 - Servicos ativos e enabled"),
    ("05_rede", "Evidencia 5 - Interfaces, rotas e portas em escuta"),
    ("06_firewall", "Evidencia 6 - Firewall (ufw/iptables)"),
    ("07_atualizacoes", "Evidencia 7 - Estado de atualizacoes"),
    ("08_logs", "Evidencia 8 - Logs e mecanismo de registro"),
]


def font(size=14, bold=False):
    candidates = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
    ]
    if bold:
        candidates = [r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\courbd.ttf"] + candidates
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_terminal(text: str, title: str, out_path: Path, max_lines: int = 28):
    lines = text.replace("\t", "    ").splitlines()
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + ["... (saida truncada para evidencia) ..."]

    f = font(13)
    f_title = font(12, bold=True)
    line_h = 18
    pad_x, pad_y = 16, 14
    title_h = 34

    tmp = Image.new("RGB", (10, 10))
    dtmp = ImageDraw.Draw(tmp)
    max_w = 0
    for ln in lines:
        bbox = dtmp.textbbox((0, 0), ln, font=f)
        max_w = max(max_w, bbox[2] - bbox[0])
    max_w = max(max_w, dtmp.textbbox((0, 0), title, font=f_title)[2])

    width = min(max(max_w + pad_x * 2, 720), 1100)
    height = title_h + pad_y * 2 + max(len(lines), 1) * line_h + 10

    img = Image.new("RGB", (width, height), "#0d1117")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, title_h], fill="#21262d")
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        x = 14 + i * 16
        draw.ellipse([x, 11, x + 10, 21], fill=color)
    draw.text((70, 9), title, font=f_title, fill="#c9d1d9")

    y = title_h + pad_y
    for ln in lines:
        color = "#c9d1d9"
        if ln.startswith("root@") or ln.startswith("machado@"):
            color = "#3fb950"
        elif "Permission denied" in ln or "Err:" in ln or "not found" in ln:
            color = "#ff7b72"
        elif ln.startswith("---") or ln.startswith("===") or "PRETTY_NAME" in ln:
            color = "#79c0ff"
        draw.text((pad_x, y), ln[:160], font=f, fill=color)
        y += line_h

    draw.rectangle([0, 0, width - 1, height - 1], outline="#30363d")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def generate_shots():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}
    for key, title in SHOT_META:
        txt = (SHOT_DIR / f"{key}.txt").read_text(encoding="utf-8", errors="replace")
        out = IMG_DIR / f"{key}.png"
        render_terminal(txt, f"Terminal - {title}", out)
        paths[key] = out
        print("shot:", out.name)
    return paths


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=15,
                         textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6, leading=18))
    s.add(ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=10,
                         textColor=ACCENT, alignment=TA_CENTER, spaceAfter=3, leading=13))
    s.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=11,
                         textColor=PRIMARY, spaceBefore=8, spaceAfter=4, leading=14))
    s.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=9.5,
                         textColor=ACCENT, spaceBefore=6, spaceAfter=3, leading=12))
    s.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=8.5,
                         alignment=TA_JUSTIFY, spaceAfter=4, leading=11))
    s.add(ParagraphStyle("Cap", fontName="Helvetica-Oblique", fontSize=7.5,
                         textColor=HexColor("#4a5568"), alignment=TA_CENTER,
                         spaceBefore=2, spaceAfter=6, leading=9))
    s.add(ParagraphStyle("Meta", fontName="Helvetica", fontSize=8.5,
                         textColor=HexColor("#4a5568"), alignment=TA_CENTER, spaceAfter=2))
    s.add(ParagraphStyle("Small", fontName="Helvetica", fontSize=7.5,
                         textColor=HexColor("#4a5568"), alignment=TA_JUSTIFY, spaceAfter=2, leading=9.5))
    s.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=7, leading=9))
    s.add(ParagraphStyle("Head", fontName="Helvetica-Bold", fontSize=7,
                         textColor=white, leading=9))
    return s


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(1)
    canvas.line(1.4*cm, A4[1]-1.15*cm, A4[0]-1.4*cm, A4[1]-1.15*cm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(ACCENT)
    canvas.drawString(1.4*cm, A4[1]-1.0*cm, "Lab 01 - Inventario Inicial + Screenshots")
    canvas.drawRightString(A4[0]-1.4*cm, A4[1]-1.0*cm, "AmazonTech")
    canvas.line(1.4*cm, 1.2*cm, A4[0]-1.4*cm, 1.2*cm)
    canvas.drawCentredString(A4[0]/2, 0.75*cm, f"Pag. {doc.page} | 28/07/2026 | Equipe: Josias, Keven, Margefson, Nattan")
    canvas.restoreState()


def kv(rows, st, c1=4.2*cm, c2=12.5*cm):
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
    target_w = width
    target_h = target_w * (h / w)
    if target_h > 9.2*cm:
        target_h = 9.2*cm
        target_w = target_h * (w / h)
    return KeepTogether([
        RLImage(str(p), width=target_w, height=target_h),
        Paragraph(f"<i>Figura - {dict(SHOT_META)[key]}</i>", st["Cap"]),
    ])


def hr():
    return HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=5)


def build(paths):
    st = styles()
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=1.4*cm, rightMargin=1.4*cm,
        topMargin=1.6*cm, bottomMargin=1.6*cm,
        title="Lab 01 - Inventario Inicial (com evidencias)",
        author="Josias Bentes, Keven Coimbra, Margefson Barros, Nattan Lobato",
    )
    story = []

    story.append(Paragraph("LABORATORIO 1 - RELATORIO COM EVIDENCIAS", st["CoverSub"]))
    story.append(Paragraph("Inventario Inicial de Seguranca", st["CoverTitle"]))
    story.append(Paragraph("Windows e Linux Hardening - Aula 1", st["CoverSub"]))
    story.append(Paragraph("AmazonTech | Servidor Linux | Debian 13.6 | 28/07/2026", st["Meta"]))
    story.append(Paragraph(
        "<b>Equipe:</b> Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato",
        st["Meta"]))
    story.append(hr())
    story.append(Paragraph(
        "Documento de entrega com inventario tecnico, diagnostico preliminar, lista de riscos, "
        "plano de investigacao e screenshots de terminal (comandos + saidas reais).",
        st["Body"]))

    # Identificacao
    story.append(Paragraph("1. Identificacao do Ambiente (Anexo A)", st["H1"]))
    story.append(kv([
        ("Nome da equipe", "Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato"),
        ("Data", "28/07/2026"),
        ("Distribuicao Linux", "Debian GNU/Linux 13 (trixie)"),
        ("Versao", "13.6 (debian_version)"),
        ("Kernel", "6.6.114.1-microsoft-standard-WSL2 (x86_64)"),
        ("Hostname", "MachadoPC"),
        ("Fuso horario", "America/Manaus (-04)"),
    ], st))
    story.append(shot(paths, "01_sistema", st))

    # Inventario usuarios
    story.append(PageBreak())
    story.append(Paragraph("2. Inventario - Usuarios e Grupos", st["H1"]))
    story.append(Paragraph(
        "Contas humanas/administrativas e de servico relevantes. Contas de login: root e usuarios "
        "com shell bash; backup com nologin (servico).",
        st["Body"]))
    story.append(shot(paths, "02_usuarios", st))
    story.append(shot(paths, "03_grupos", st))

    # Servicos
    story.append(Paragraph("3. Inventario - Servicos", st["H1"]))
    story.append(Paragraph(
        "Superficie de servicos locais relativamente enxuta. Sem openssh-server em execucao. "
        "cron e journald ativos.",
        st["Body"]))
    story.append(shot(paths, "04_servicos", st))

    # Rede
    story.append(PageBreak())
    story.append(Paragraph("4. Inventario - Rede e Firewall", st["H1"]))
    story.append(Paragraph(
        "Interfaces lo/eth0; portas em escuta tipicas do ambiente WSL (DNS interno). "
        "Firewall: ufw/iptables sem politica evidenciada de forma completa no inventario inicial.",
        st["Body"]))
    story.append(shot(paths, "05_rede", st))
    story.append(shot(paths, "06_firewall", st))

    # Updates e logs
    story.append(PageBreak())
    story.append(Paragraph("5. Inventario - Atualizacoes e Logs", st["H1"]))
    story.append(Paragraph(
        "No inventario inicial havia pacotes pendentes; apos apt-get full-upgrade (mesma data), "
        "a evidencia atual mostra lista de upgrades vazia e versoes atualizadas de sudo/systemd/libc6/openssl. "
        "Logs: journald ativo; rsyslog ativo; politica PASS_MAX_DAYS ainda permissiva no login.defs.",
        st["Body"]))
    story.append(shot(paths, "07_atualizacoes", st))
    story.append(shot(paths, "08_logs", st))

    # Checklist
    story.append(Paragraph("6. Checklist do Inventario", st["H1"]))
    story.append(grid(
        ["Item", "Status", "Evidencia"],
        [
            ["Distribuicao Linux identificada", "SIM", "Fig. 1 /etc/os-release"],
            ["Versao do Kernel registrada", "SIM", "Fig. 1 uname/hostnamectl"],
            ["Hostname identificado", "SIM", "MachadoPC"],
            ["Usuarios listados", "SIM", "Fig. 2"],
            ["Grupos identificados", "SIM", "Fig. 3"],
            ["Contas administrativas verificadas", "SIM", "grupo sudo"],
            ["Servicos ativos registrados", "SIM", "Fig. 4"],
            ["Portas abertas identificadas", "SIM", "Fig. 5 ss -tulnp"],
            ["Interfaces de rede documentadas", "SIM", "Fig. 5 ip -br addr"],
            ["Firewall analisado", "SIM", "Fig. 6 (parcial/sem regras)"],
            ["Atualizacoes verificadas", "SIM", "Fig. 7"],
            ["Logs localizados", "SIM", "Fig. 8"],
        ],
        st, [6.0*cm, 2.2*cm, 8.5*cm], OK
    ))

    # Diagnostico
    story.append(PageBreak())
    story.append(Paragraph("7. Diagnostico Preliminar (Questoes 1 a 5)", st["H1"]))
    story.append(Paragraph(
        "<b>Q1 - Maiores riscos:</b> ausencia de politica de firewall evidenciada; "
        "PASS_MAX_DAYS=99999; dependencia historica de patches (corrigida apos full-upgrade); "
        "plataforma WSL a validar para producao corporativa.<br/><br/>"
        "<b>Q2 - Informacoes ainda necessarias:</b> escopo de aplicacoes do negocio; politica formal "
        "de atualizacao; topologia de rede; requisitos da auditoria externa; homologacao da plataforma.<br/><br/>"
        "<b>Q3 - Configuracao inadequada?</b> Sim, com evidencia: firewall nao comprovado; "
        "politica de senha permissiva; (inicialmente) patches pendentes.<br/><br/>"
        "<b>Q4 - Pronto para producao?</b> Ainda <b>nao</b> de forma plena: embora updates tenham sido "
        "aplicados e a superficie de escuta seja reduzida, faltam controles de firewall e endurecimento "
        "de identidade/senha alinhados a producao.<br/><br/>"
        "<b>Q5 - Primeira acao em 1h:</b> no inventario inicial seria aplicar patches; isso ja foi feito. "
        "Proximo ganho: definir firewall default-deny e revisar politica de senha/sudo.",
        st["Body"]))

    story.append(Paragraph("8. Lista Preliminar de Riscos", st["H1"]))
    story.append(grid(
        ["Risco", "Severidade", "Evidencia"],
        [
            ["Firewall omitido / nao comprovado", "Alta", "Fig. 6"],
            ["Politica de senha fraca (PASS_MAX_DAYS=99999)", "Media-Alta", "Fig. 8 login.defs"],
            ["Plataforma WSL em contexto produtivo", "Media", "Fig. 1 kernel microsoft-WSL2"],
            ["Gestao de tempo (NTP service n/a)", "Baixa-Media", "Fig. 1 timedatectl"],
        ],
        st, [6.5*cm, 3.0*cm, 7.2*cm], WARN
    ))

    story.append(Paragraph("9. Plano de Investigacao / Recomendacoes Iniciais", st["H1"]))
    story.append(Paragraph(
        "<b>R1</b> - Manter ciclo de patch (ja executado full-upgrade nesta data).<br/>"
        "<b>R2</b> - Implementar firewall default-deny com portas do negocio.<br/>"
        "<b>R3</b> - Endurecer identidade (PASS_MAX_DAYS, sudo, contas) - detalhado no Lab 02.<br/><br/>"
        "Proximas aulas: identidades/privilegios, permissoes, ACL e auditoria continua.",
        st["Body"]))

    story.append(Paragraph("10. Fechamento", st["H1"]))
    story.append(Paragraph(
        "Mais faceis: SO, kernel, hostname, usuarios, servicos e portas.<br/>"
        "Mais dificeis: estado real do firewall e correlacao de erros do journal.<br/>"
        "Surpresa: discurso de 'ambiente seguro' vs gaps de hardening evidentes.<br/>"
        "Prioridade de hardening: firewall + identidade/senha, mantendo patches em dia.",
        st["Body"]))
    story.append(Paragraph(
        "Screenshots: evidencias/shots/img/ | Saidas brutas: evidencias/shots/*.txt e evidencias/inventory_raw.txt",
        st["Small"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("PDF:", OUT)


if __name__ == "__main__":
    paths = generate_shots()
    build(paths)
    shutil.copy2(OUT, DL)
    print("Download:", DL)
