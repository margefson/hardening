#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 07B PDFs: Ordem de Servico + Windows Defender Firewall."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab07b")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab07B_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab07B_Windows_Firewall_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab07B_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab07B_Windows_Firewall_PREENCHIDO.pdf")

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
    ("01_ambiente", "Evidencia 1 - Ambiente WIN-ADM-01"),
    ("02_perfis_firewall", "Evidencia 2 - Perfis Domain/Private/Public"),
    ("03_console_avancado", "Evidencia 3 - Console avancado (wf.msc)"),
    ("04_regras_amostra", "Evidencia 4 - Regras (amostra)"),
    ("05_powershell_admin", "Evidencia 5 - Get-NetFirewallProfile/Rule"),
    ("06_exportacao", "Evidencia 6 - Exportacao de politica"),
    ("07_regras_habilitadas", "Evidencia 7 - Regras habilitadas"),
    ("08_consolidacao", "Evidencia 8 - Consolidacao / parecer"),
]


def font(size=12, bold=False):
    cands = [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf"]
    if bold:
        cands = [r"C:\Windows\Fonts\consolab.ttf"] + cands
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_terminal(text, title, out_path, max_lines=36):
    lines = text.replace("\t", "    ").splitlines()
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + ["... (saida truncada) ..."]
    f, ft = font(12), font(11, True)
    line_h, pad_x, pad_y, title_h = 17, 14, 12, 34
    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    max_w = max((d.textbbox((0, 0), ln, font=f)[2] for ln in lines), default=700)
    max_w = max(max_w, d.textbbox((0, 0), title, font=ft)[2])
    w = min(max(max_w + pad_x * 2, 780), 1150)
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
        if ln.startswith("PS>") or ln.startswith("===") or ln.startswith("["):
            color = "#3fb950"
        elif "True" in ln or "Enabled" in ln or "ATENDE" in ln or "Allow" in ln:
            color = "#79c0ff"
        elif "False" in ln or "eleva" in ln.lower() or "ressalvas" in ln.lower() or "Block" in ln:
            color = "#ff7b72"
        elif ln.startswith("#") or ln.startswith("-") or ln.startswith("  "):
            color = "#8b949e"
        draw.text((pad_x, y), ln[:175], font=f, fill=color)
        y += line_h
    draw.rectangle([0, 0, w - 1, h - 1], outline="#30363d")
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
    s.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=12.5,
                         textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6, leading=15))
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
        canvas.drawRightString(A4[0]-1.4*cm, A4[1]-1.0*cm, "AmazonTech WIN-ADM-01")
        canvas.line(1.4*cm, 1.2*cm, A4[0]-1.4*cm, 1.2*cm)
        canvas.drawCentredString(A4[0]/2, 0.75*cm,
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lab 07B")
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
                            title="Lab 07B - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 07B", st["CoverTitle"]))
    story.append(Paragraph("Administracao e Validacao do Windows Defender Firewall", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        "Status: CONCLUIDA | Somente consultas (sem alteracao permanente de regras)",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Estacao", "WIN-ADM-01 (MachadoPC)"),
        ("SO", "Microsoft Windows 11 Home Single Language (build 26200)"),
        ("Disciplina", "Criptografia e Trusted Computing / Windows Hardening III"),
        ("Tipo", "Validacao das politicas de comunicacao (Firewall)"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Resultado", st["H1"]))
    story.append(grid(
        ["Situacao", "Resultado", "Status"],
        [
            ["Perfis Domain/Private/Public", "Todos Enabled=True; rede ativa = Public", "Validado"],
            ["Servico MpsSvc / wf.msc", "Running Automatic; wf.msc presente", "OK"],
            ["Inventario de regras", "552 totais (317 in / 235 out); 312 habilitadas", "Inventariado"],
            ["Amostra de regras", "1 inbound + 1 outbound documentadas", "OK"],
            ["PowerShell admin", "Get-NetFirewallProfile / Rule executados", "OK"],
            ["Exportacao .wfw", "Identificada; exige elevacao (nao aplicada)", "Limitado"],
        ],
        st, [4.2*cm, 9.3*cm, 2.7*cm], WARN
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "02_perfis_firewall", st))
    story.append(PageBreak())
    story.append(shot(paths, "03_console_avancado", st))
    story.append(shot(paths, "04_regras_amostra", st))
    story.append(PageBreak())
    story.append(shot(paths, "05_powershell_admin", st))
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Firewall do host habilitado nos tres perfis", "SIM"],
            ["2. Perfis de rede identificados e documentados", "SIM"],
            ["3. Regras de entrada/saida interpretadas", "SIM"],
            ["4. Console avancado (wf.msc) / equivalente PS", "SIM"],
            ["5. Consulta administrativa PowerShell", "SIM"],
            ["6. Recurso de exportacao identificado", "SIM (sem elevacao)"],
            ["7. Evidencias tecnicas registradas", "SIM"],
            ["8. Nenhuma regra alterada permanentemente", "SIM"],
        ],
        st, [13.2*cm, 3.5*cm], OK
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - firewall apto na camada de comunicacao (com revisao de excecoes)"),
        ("Documento tecnico", "Lab07B_Windows_Firewall_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 07B - Ordem de Servico"),
              onLaterPages=footer("Lab 07B - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 07B - Windows Firewall", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 07B", st["CoverTitle"]))
    story.append(Paragraph("Administracao e Validacao do Windows Defender Firewall", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Estacao: WIN-ADM-01",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Equipe", TEAM),
        ("Data", DATE),
        ("Laboratorio", "07B - Windows Defender Firewall"),
        ("Sistema Operacional", "Microsoft Windows 11 Home Single Language"),
        ("Versao / Build", "10.0.26200 (build 26200)"),
        ("Hostname", "MachadoPC (WIN-ADM-01)"),
    ], st))

    story.append(Paragraph("2. Objetivo", st["H1"]))
    story.append(Paragraph(
        "Validar a configuracao do Windows Defender Firewall como camada de controle das "
        "<b>comunicacoes</b> do endpoint: identificar perfis Domain/Private/Public, interpretar "
        "regras de entrada/saida, explorar wf.msc, consultar via PowerShell e reconhecer a "
        "exportacao de politica — sem modificar permanentemente regras (restricao da OS).",
        st["Body"]))

    story.append(Paragraph("3. Ferramentas Utilizadas", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade"],
        [
            ["Windows Defender Firewall", "Interface basica / estado dos perfis"],
            ["wf.msc (Advanced Security)", "Regras, IPsec, monitoramento"],
            ["Get-NetFirewallProfile", "Estado e acoes padrao por perfil"],
            ["Get-NetFirewallRule (+ filtros)", "Inventario e propriedades de regras"],
            ["Get-NetConnectionProfile", "Categoria da rede ativa"],
            ["Get-NetIPsecRule", "Seguranca de conexao / IPsec"],
            ["netsh advfirewall export", "Backup/exportacao de politica (.wfw)"],
        ],
        st, [6.2*cm, 10.5*cm]
    ))

    story.append(Paragraph("4. Evidencias Coletadas", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_perfis_firewall", st))
    story.append(shot(paths, "03_console_avancado", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_regras_amostra", st))
    story.append(shot(paths, "05_powershell_admin", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_exportacao", st))
    story.append(shot(paths, "07_regras_habilitadas", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("5. Resultados Obtidos", st["H1"]))
    story.append(Paragraph("5.1 Perfis (Atividade 1)", st["H2"]))
    story.append(Paragraph(
        "Domain, Private e Public com <b>Enabled=True</b>. Defaults In/Out = NotConfigured "
        "(comportamento padrao do SO). Servico <b>MpsSvc</b> Running/Automatic; wf.msc presente. "
        "Rede ativa: Wi-Fi classificada como <b>Public</b> (mais restritiva — adequado para rede "
        "nao corporativa/desconhecida).",
        st["Body"]))

    story.append(Paragraph("5.2 Console avancado e volume de regras (Ativ. 2)", st["H2"]))
    story.append(Paragraph(
        "Inventario equivalente a wf.msc: <b>552</b> regras (317 inbound / 235 outbound); "
        "312 habilitadas (169 in / 143 out). IPsec/Connection Security: 0 (tipico em workgroup). "
        "Monitoramento reflete perfil Public corrente.",
        st["Body"]))

    story.append(Paragraph("5.3 Regras amostradas (Ativ. 3)", st["H2"]))
    story.append(Paragraph(
        "<b>Regra 1 (Entrada):</b> Rede Principal - IPv6 (IPv6-Entrada) — Inbound Allow, perfil Any, "
        "programa System, protocolo 41.<br/>"
        "<b>Regra 2 (Saida):</b> Descoberta de Rede (SSDP-Saida) — Outbound Allow, perfil Private, "
        "svchost.exe, UDP, remoto LocalSubnet.<br/>"
        "Essas amostras ilustram como Allow + escopo amplo (Any) vs. LocalSubnet altera a superficie.",
        st["Body"]))

    story.append(Paragraph("5.4 PowerShell e exportacao (Ativ. 4-5)", st["H2"]))
    story.append(Paragraph(
        "Get-NetFirewallProfile e Get-NetFirewallRule | Select -First 10 permitem auditoria "
        "rapida sem GUI. Exportacao via wf.msc (Export Policy) ou "
        "<font face='Courier'>netsh advfirewall export</font> serve a backup, padronizacao e "
        "comparacao de drift; nesta estacao a exportacao <b>exigiu elevacao</b> e nao foi "
        "gravada — recurso identificado e documentado conforme a OS.",
        st["Body"]))

    story.append(Paragraph("6. Questoes de Encerramento", st["H1"]))
    story.append(Paragraph(
        "<b>Q1 - Papel do Firewall:</b> segunda camada da protecao de endpoints (apos Defender): "
        "controla o que entra/sai do host, reduzindo superficie alem do antimalware.<br/><br/>"
        "<b>Q2 - Perfis habilitados:</b> Domain, Private e Public — todos Enabled=True; "
        "conexao ativa em Public.<br/><br/>"
        "<b>Q3 - Entrada vs saida:</b> Inbound filtra conexoes iniciadas de fora para o host; "
        "Outbound filtra trafego originado no host. Defaults tipicos: bloquear entrada nao "
        "solicitada e permitir saida (ajustavel por politica).<br/><br/>"
        "<b>Q4 - Limitacoes:</b> export .wfw sem elevacao; edicao Home limita GPO central; "
        "volume alto de regras (552) dificulta revisao manual; evidencias via PowerShell "
        "(equivalente funcional a wf.msc).<br/><br/>"
        "<b>Q5 - Recomendacoes:</b> inventariar/remover excecoes temporarias; baseline "
        "GPO/Intune; habilitar logging (LogBlocked); classificar redes corporativas como "
        "Domain/Private; revisar regras Allow Any; export periodico da politica aprovada.",
        st["Body"]))

    story.append(Paragraph("7. Dificuldades Encontradas", st["H1"]))
    story.append(Paragraph(
        "netsh advfirewall export retornou erro de elevacao. Defaults NotConfigured exigem "
        "interpretacao (nao exibem Block/Allow literal). Grande numero de regras do fabricante "
        "exige amostragem em vez de analise linha a linha. Nenhuma regra foi alterada.",
        st["Body"]))

    story.append(Paragraph("8. Conclusao Tecnica / Parecer", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Estacao", "WIN-ADM-01 / MachadoPC"),
        ("Escopo", "Validacao Windows Defender Firewall (somente leitura)"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "O endpoint possui firewall <b>operacional</b> nos tres perfis, servico ativo e inventario "
        "documentado. A classificacao Public da rede Wi-Fi e positiva para exposicao casual. "
        "O volume de regras habilitadas e a ausencia de exportacao privilegiada indicam necessidade "
        "de governanca (baseline + revisao de excecoes) antes da padronizacao corporativa definitiva. "
        "Complementa o Lab 07A (Defender) na defesa em profundidade.<br/>"
        "<b>Parecer:</b> [X] <b>APTO PARA HOMOLOGACAO DA CAMADA FIREWALL</b> neste endpoint, "
        "com recomendacao de revisao periodica de regras e logging.<br/>"
        f"<b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("Checklist Final", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["Perfis Domain/Private/Public analisados", "SIM"],
            ["Console avancado / inventario de regras", "SIM"],
            ["Regras de entrada e saida interpretadas", "SIM"],
            ["Consultas PowerShell documentadas", "SIM"],
            ["Exportacao de politica identificada", "SIM"],
            ["Questoes de encerramento respondidas", "SIM"],
            ["Nenhuma regra alterada permanentemente", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))

    doc.build(story, onFirstPage=footer("Lab 07B - Windows Firewall + Screenshots"),
              onLaterPages=footer("Lab 07B - Windows Firewall + Screenshots"))
    print("LAB OK")


if __name__ == "__main__":
    paths = generate_shots()
    build_os(paths)
    build_lab(paths)
    shutil.copy2(OUT_OS, DL_OS)
    shutil.copy2(OUT_LAB, DL_LAB)
    print("Downloads:")
    print(DL_OS)
    print(DL_LAB)
