#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 07E PDFs: Ordem de Servico + Hardening de Servicos."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab07e")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab07E_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab07E_Hardening_Servicos_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab07E_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab07E_Hardening_Servicos_PREENCHIDO.pdf")

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
    ("02_servicos", "Evidencia 2 - Servicos Windows"),
    ("03_startup", "Evidencia 3 - Programas de inicializacao"),
    ("04_recursos_opcionais", "Evidencia 4 - Recursos opcionais"),
    ("05_powershell_admin", "Evidencia 5 - Get-Service / OptionalFeature"),
    ("06_superficie_ataque", "Evidencia 6 - Superficie de ataque"),
    ("07_plano_hardening", "Evidencia 7 - Plano preliminar"),
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
        if ln.startswith("PS>") or ln.startswith("===") or ln.startswith("---"):
            color = "#3fb950"
        elif "Disabled" in ln or "MANTER" in ln or "WinDefend" in ln or "CONCLUIDA" in ln:
            color = "#79c0ff"
        elif "eleva" in ln.lower() or "Running" in ln and ("Spooler" in ln or "Adobe" in ln or "PDF24" in ln or "WSL" in ln):
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
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lab 07E")
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
                            title="Lab 07E - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 07E", st["CoverTitle"]))
    story.append(Paragraph("Avaliacao de Hardening de Servicos", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        "Status: CONCLUIDA | Avaliativo (nenhum servico desabilitado)",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Estacao", "WIN-ADM-01 (MachadoPC)"),
        ("SO", "Microsoft Windows 11 Home Single Language (build 26200)"),
        ("Disciplina", "Criptografia e Trusted Computing / Windows Hardening III"),
        ("Tipo", "Avaliacao de superficie de ataque / Hardening de servicos"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Resultado", st["H1"]))
    story.append(grid(
        ["Situacao", "Resultado", "Status"],
        [
            ["Servicos Windows", "291 total; 126 Running; 94 Automatic; RemoteRegistry Disabled", "Inventariado"],
            ["Startup", "5 entradas (Teams, Adobe, Edge, SecurityHealth, PDF24)", "Revisado"],
            ["Recursos opcionais", "GUI identificada; Get-WindowsOptionalFeature exige elevacao", "Limitado"],
            ["Superficie extra", "Adobe/PDF24/PostgreSQL/VMware/WSL Automatic Running", "Identificado"],
            ["Plano preliminar", "Tabela de recomendacoes elaborada (sem aplicar)", "Entregue"],
            ["Controles 07A-07D", "WinDefend/MpsSvc mantidos como nucleo", "Preservado"],
        ],
        st, [4.2*cm, 9.3*cm, 2.7*cm], WARN
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "02_servicos", st))
    story.append(PageBreak())
    story.append(shot(paths, "03_startup", st))
    story.append(shot(paths, "06_superficie_ataque", st))
    story.append(PageBreak())
    story.append(shot(paths, "07_plano_hardening", st))
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Servicos em execucao identificados", "SIM"],
            ["2. Programas de inicializacao analisados", "SIM"],
            ["3. Funcionalidades opcionais localizadas", "SIM (com limitacao)"],
            ["4. Conceito de superficie de ataque aplicado", "SIM"],
            ["5. Oportunidades de Hardening reconhecidas", "SIM"],
            ["6. Plano preliminar elaborado", "SIM"],
            ["7. Evidencias tecnicas registradas", "SIM"],
            ["8. Nenhum servico desabilitado nesta OS", "SIM"],
        ],
        st, [13.2*cm, 3.5*cm], OK
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - avaliacao de Hardening; plano preliminar entregue"),
        ("Documento tecnico", "Lab07E_Hardening_Servicos_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 07E - Ordem de Servico"),
              onLaterPages=footer("Lab 07E - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 07E - Hardening de Servicos", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 07E", st["CoverTitle"]))
    story.append(Paragraph("Avaliacao de Hardening de Servicos", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Estacao: WIN-ADM-01",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Equipe", TEAM),
        ("Data", DATE),
        ("Laboratorio", "07E - Hardening de Servicos"),
        ("Sistema Operacional", "Microsoft Windows 11 Home Single Language"),
        ("Versao / Build", "10.0.26200 (build 26200)"),
        ("Hostname", "MachadoPC (WIN-ADM-01)"),
    ], st))

    story.append(Paragraph("2. Objetivo", st["H1"]))
    story.append(Paragraph(
        "Avaliar a configuracao atual do endpoint sob a otica do Hardening: inventariar "
        "servicos, programas de inicializacao e recursos opcionais; reconhecer oportunidades "
        "de reducao da <b>superficie de ataque</b>; e elaborar um plano preliminar — "
        "<b>sem desabilitar</b> qualquer servico nesta Ordem de Servico.",
        st["Body"]))

    story.append(Paragraph("3. Ferramentas Utilizadas", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade"],
        [
            ["services.msc / Get-Service", "Inventario de servicos e StartType"],
            ["Win32_Service (CIM)", "Path/StartMode dos servicos"],
            ["Win32_StartupCommand + Run keys", "Programas de inicializacao"],
            ["msconfig / Task Manager Startup", "Impacto de boot (referencia GUI)"],
            ["optionalfeatures.exe", "Recursos opcionais (GUI)"],
            ["Get-WindowsOptionalFeature", "Features Online (requer elevacao)"],
            ["Plano preliminar (tabela)", "Recomendacoes sem aplicar mudancas"],
        ],
        st, [6.2*cm, 10.5*cm]
    ))

    story.append(Paragraph("4. Evidencias Coletadas", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_servicos", st))
    story.append(shot(paths, "03_startup", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_recursos_opcionais", st))
    story.append(shot(paths, "05_powershell_admin", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_superficie_ataque", st))
    story.append(shot(paths, "07_plano_hardening", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("5. Resultados Obtidos", st["H1"]))
    story.append(Paragraph("5.1 Servicos (Atividade 1)", st["H2"]))
    story.append(Paragraph(
        "<b>291</b> servicos (126 Running / 165 Stopped); StartType: Manual 192, Automatic 94, "
        "Disabled 5. Amostra analitica:<br/>"
        "1) <b>WinDefend</b> — Running/Automatic — motor Defender (MANTER).<br/>"
        "2) <b>Spooler</b> — Running/Automatic — impressao; revisar se host sem impressora.<br/>"
        "3) <b>RemoteRegistry</b> — Stopped/Disabled — superficie remota ja mitigada.",
        st["Body"]))

    story.append(Paragraph("5.2 Startup e recursos (Ativ. 2-3)", st["H2"]))
    story.append(Paragraph(
        "Startup: Teams, Adobe Acrobat Synchronizer, Edge AutoLaunch, SecurityHealth, PDF24. "
        "Candidatos a revisao de impacto: Adobe Sync e PDF24 (nao essenciais ao core). "
        "Recursos opcionais: Get-WindowsOptionalFeature exigiu elevacao; optionalfeatures.exe "
        "presente; WSLService Running/Automatic; pacotes Containers/ApplicationGuard no CBS.",
        st["Body"]))

    story.append(Paragraph("5.3 Superficie e PowerShell (Ativ. 4)", st["H2"]))
    story.append(Paragraph(
        "Servicos Automatic fora de System32 incluem AdobeARM, PDF24, PostgreSQL 18, "
        "VMware Auth/USB e WSL — justificaveis em lab/dev, mas devem constar do inventario "
        "corporativo. PowerShell espelha services.msc com filtros/export para auditoria em massa.",
        st["Body"]))

    story.append(Paragraph("6. Plano Preliminar de Hardening", st["H1"]))
    story.append(grid(
        ["Item", "Situacao", "Recomendacao"],
        [
            ["RemoteRegistry", "Disabled/Stopped", "Manter Disabled"],
            ["Spooler", "Running/Automatic", "Revisar; desabilitar se sem impressao"],
            ["Xbox*/WMPNetwork", "Stopped/Manual", "Manter desnecessarios off"],
            ["Startup Adobe/PDF24", "Habilitados", "Remover se sem demanda"],
            ["SMB1/Telnet/TFTP", "Verificar sob elevacao", "Remover se Enabled"],
            ["WSL/Containers", "WSL ativo", "Restringir a perfis autorizados"],
            ["PostgreSQL/VMware", "Auto Running", "Justificar no inventario"],
            ["WinDefend/MpsSvc", "Nucleo 07A/07B", "MANTER ativos"],
        ],
        st, [4.5*cm, 5.5*cm, 6.7*cm], WARN
    ))
    story.append(Paragraph(
        "Documento: lab07e/evidencias/docs/Plano_Preliminar_Hardening_Servicos.txt",
        st["Small"]))

    story.append(Paragraph("7. Questoes de Encerramento", st["H1"]))
    story.append(Paragraph(
        "<b>Q1 - Superficie de ataque:</b> conjunto de servicos, portas, features, startup e "
        "componentes pelos quais um atacante pode interagir; reduzir = remover o desnecessario.<br/><br/>"
        "<b>Q2 - Processo continuo:</b> softwares e necessidades mudam; sem revisao periodica "
        "o hardening degrada (drift).<br/><br/>"
        "<b>Q3 - Analise detalhada:</b> Spooler, startup de terceiros, WSL/Containers, "
        "servicos Auto fora System32, features legado (SMB1/Telnet) sob elevacao.<br/><br/>"
        "<b>Q4 - Limitacoes:</b> Get-WindowsOptionalFeature sem elevacao; edicao Home; "
        "proibicao de desabilitar servicos nesta OS (apenas plano).<br/><br/>"
        "<b>Q5 - Recomendacoes Diretoria:</b> ciclo trimestral de Hardening; baseline "
        "GPO/Intune; change control; manter 07A-07D; priorizar plano preliminar.",
        st["Body"]))

    story.append(Paragraph("8. Dificuldades Encontradas", st["H1"]))
    story.append(Paragraph(
        "Optional Features e Capabilities exigiram administrador. Inventario CBS e indicadores "
        "de servico (WSL) compensaram parcialmente. Nenhuma alteracao de StartType foi feita.",
        st["Body"]))

    story.append(Paragraph("9. Conclusao Tecnica / Parecer", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Estacao", "WIN-ADM-01 / MachadoPC"),
        ("Escopo", "Avaliacao Hardening de servicos (sem desabilitar)"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "A avaliacao confirma nucleo de protecao preservado (Defender/Firewall) e "
        "oportunidades claras de menor funcionalidade (startup, Spooler, WSL, servicos de "
        "terceiros). O Hardening encerra o Programa da Aula 7 como <b>processo continuo</b>, "
        "nao como checklist unico.<br/>"
        "<b>Parecer:</b> [X] <b>PROGRAMA AULA 7 CONCLUIDO (07A-07E) — AVALIACAO DE "
        "HARDENING APTA</b>; implantacao do plano preliminar mediante aceite da Diretoria.<br/>"
        f"<b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("Checklist Final + Encerramento 07A-07E", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["Servicos inventariados (3+ descritos)", "SIM"],
            ["Startup analisado", "SIM"],
            ["Recursos opcionais localizados", "SIM"],
            ["Consulta PowerShell documentada", "SIM"],
            ["Plano preliminar de Hardening", "SIM"],
            ["Questoes de encerramento respondidas", "SIM"],
            ["Nenhum servico desabilitado nesta OS", "SIM"],
            ["Ciclo Aula 7 (07A+07B+07C+07D+07E)", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))

    doc.build(story, onFirstPage=footer("Lab 07E - Hardening Servicos + Screenshots"),
              onLaterPages=footer("Lab 07E - Hardening Servicos + Screenshots"))
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
