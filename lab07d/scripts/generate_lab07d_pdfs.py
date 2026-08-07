#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 07D PDFs: Ordem de Servico + Administracao Segura com PowerShell."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab07d")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab07D_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab07D_PowerShell_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab07D_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab07D_PowerShell_PREENCHIDO.pdf")

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
    ("02_versao_powershell", "Evidencia 2 - Versao PowerShell"),
    ("03_ajuda_comandos", "Evidencia 3 - Get-Help / Get-Command"),
    ("04_servicos_processos", "Evidencia 4 - Get-Service / Get-Process"),
    ("05_execution_policy", "Evidencia 5 - Execution Policy"),
    ("06_computerinfo", "Evidencia 6 - Get-ComputerInfo"),
    ("07_integracao_labs", "Evidencia 7 - Integracao Defender/Firewall"),
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
        elif "RemoteSigned" in ln or "True" in ln or "ATENDE" in ln or "5.1." in ln:
            color = "#79c0ff"
        elif "Bypass" in ln or "False" in ln or "Undefined" in ln and "LocalMachine" in ln:
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
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lab 07D")
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
                            title="Lab 07D - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 07D", st["CoverTitle"]))
    story.append(Paragraph("Administracao Segura com PowerShell", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        "Status: CONCLUIDA | Exploratorio (sem alteracao permanente)",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Estacao", "WIN-ADM-01 (MachadoPC)"),
        ("SO", "Microsoft Windows 11 Home Single Language (build 26200)"),
        ("Disciplina", "Criptografia e Trusted Computing / Windows Hardening III"),
        ("Tipo", "Validacao da plataforma PowerShell (automacao/governanca)"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Resultado", st["H1"]))
    story.append(grid(
        ["Situacao", "Resultado", "Status"],
        [
            ["Ambiente PowerShell", "PS 5.1.26100.8875 Desktop; Windows Terminal OK", "Validado"],
            ["Ajuda / Get-Command", "Get-Help OK; ~1731 comandos (643 cmdlets)", "OK"],
            ["Servicos / Processos", "Amostras Running + top CPU documentadas", "OK"],
            ["Execution Policy", "CurrentUser=RemoteSigned; Process Bypass so na captura", "Revisado"],
            ["Get-ComputerInfo", "Win11 Home; UEFI; HyperVisorPresent=True", "OK"],
            ["Integracao 07A/07B", "MpComputerStatus + NetFirewallProfile via PS", "OK"],
        ],
        st, [4.2*cm, 9.3*cm, 2.7*cm], OK
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "02_versao_powershell", st))
    story.append(PageBreak())
    story.append(shot(paths, "05_execution_policy", st))
    story.append(shot(paths, "06_computerinfo", st))
    story.append(PageBreak())
    story.append(shot(paths, "07_integracao_labs", st))
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Recursos administrativos do PowerShell identificados", "SIM"],
            ["2. Cmdlets administrativos interpretados", "SIM"],
            ["3. Execution Policy compreendida", "SIM"],
            ["4. Mecanismos de ajuda explorados", "SIM"],
            ["5. Informacoes do SO validadas", "SIM"],
            ["6. Integracao com mecanismos 07A/07B demonstrada", "SIM"],
            ["7. Evidencias tecnicas registradas", "SIM"],
            ["8. Nenhuma configuracao permanente alterada", "SIM"],
        ],
        st, [13.2*cm, 3.5*cm], OK
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - PowerShell apto como plataforma de admin segura"),
        ("Documento tecnico", "Lab07D_PowerShell_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 07D - Ordem de Servico"),
              onLaterPages=footer("Lab 07D - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 07D - PowerShell", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 07D", st["CoverTitle"]))
    story.append(Paragraph("Administracao Segura com PowerShell", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Estacao: WIN-ADM-01",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Equipe", TEAM),
        ("Data", DATE),
        ("Laboratorio", "07D - Administracao Segura com PowerShell"),
        ("Sistema Operacional", "Microsoft Windows 11 Home Single Language"),
        ("Versao / Build", "10.0.26200 (build 26200)"),
        ("Hostname", "MachadoPC (WIN-ADM-01)"),
    ], st))

    story.append(Paragraph("2. Objetivo", st["H1"]))
    story.append(Paragraph(
        "Compreender o PowerShell como plataforma de administracao <b>segura, padronizada "
        "e auditavel</b> da infraestrutura Windows: explorar ambiente, ajuda, cmdlets "
        "administrativos, Execution Policy e integracao com Defender/Firewall — sem alterar "
        "configuracoes permanentes (restricao da OS).",
        st["Body"]))

    story.append(Paragraph("3. Ferramentas Utilizadas", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade"],
        [
            ["Windows PowerShell 5.1", "Shell administrativo Desktop"],
            ["Windows Terminal (wt.exe)", "Host moderno (disponivel)"],
            ["Get-Help / Get-Command", "Documentacao e inventario de comandos"],
            ["Get-Service / Get-Process", "Estado operacional do host"],
            ["Get-ExecutionPolicy (-List)", "Governanca de execucao de scripts"],
            ["Get-ComputerInfo", "Inventario do SO / hardware"],
            ["Get-MpComputerStatus", "Integracao Lab 07A (Defender)"],
            ["Get-NetFirewallProfile", "Integracao Lab 07B (Firewall)"],
        ],
        st, [6.2*cm, 10.5*cm]
    ))

    story.append(Paragraph("4. Evidencias Coletadas", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_versao_powershell", st))
    story.append(shot(paths, "03_ajuda_comandos", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_servicos_processos", st))
    story.append(shot(paths, "05_execution_policy", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_computerinfo", st))
    story.append(shot(paths, "07_integracao_labs", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("5. Resultados Obtidos", st["H1"]))
    story.append(Paragraph("5.1 Ambiente (Atividade 1)", st["H2"]))
    story.append(Paragraph(
        "Windows PowerShell <b>5.1.26100.8875</b> (Edition Desktop, ConsoleHost). "
        "Windows Terminal disponivel (wt.exe). PowerShell 7 (pwsh) nao instalado — "
        "opcional para frota corporativa futura.",
        st["Body"]))

    story.append(Paragraph("5.2 Ajuda e inventario (Atividade 2)", st["H2"]))
    story.append(Paragraph(
        "Get-Help Get-Service retornou sintaxe/synopsis do modulo Management. "
        "Get-Command listou ~<b>1731</b> comandos (991 Function, 643 Cmdlet, alem de aliases). "
        "Esses recursos substituem documentacao externa ad-hoc e padronizam o onboarding "
        "dos administradores AmazonTech.",
        st["Body"]))

    story.append(Paragraph("5.3 Servicos/processos e Execution Policy (Ativ. 3-4)", st["H2"]))
    story.append(Paragraph(
        "Amostras de servicos Running (incl. WinDefend/MpsSvc) e processos por CPU. "
        "Execution Policy: <b>CurrentUser=RemoteSigned</b> (boa pratica); Machine/User Policy "
        "Undefined; <b>Process=Bypass</b> apenas na sessao de captura "
        "(-ExecutionPolicy Bypass), sem Set-ExecutionPolicy e sem mudanca em LocalMachine.",
        st["Body"]))

    story.append(Paragraph("5.4 Integracao administrativa (Atividade 5)", st["H2"]))
    story.append(Paragraph(
        "Get-ComputerInfo: Win11 Home, build 26200, UEFI, HyperVisorPresent=True, WORKGROUP. "
        "No mesmo shell: Defender (AV/RTP/assinatura 1.457.40.0) e Firewall (3 perfis Enabled) "
        "— demonstrando que o PowerShell integra Labs 07A–07C em um unico fluxo auditavel.",
        st["Body"]))

    story.append(Paragraph("6. Questoes de Encerramento", st["H1"]))
    story.append(Paragraph(
        "<b>Q1 - Papel do PowerShell:</b> camada de administracao/governanca que padroniza "
        "consultas e automacoes sobre Defender, Firewall, BitLocker e o SO, com evidencias "
        "reproduziveis.<br/><br/>"
        "<b>Q2 - Execution Policy:</b> reduz execucao acidental/maliciosa de scripts; "
        "RemoteSigned/AllSigned equilibra produtividade e controle; Bypass permanente "
        "aumenta risco operacional.<br/><br/>"
        "<b>Q3 - Automacao vs manual:</b> repetibilidade, menor erro humano, versionamento, "
        "escala multi-host e trilhas de auditoria.<br/><br/>"
        "<b>Q4 - Limitacoes:</b> edicao Home limita GPO/JEA corporativo; help local sem "
        "Update-Help completo; Bypass de processo na captura; pwsh 7 ausente.<br/><br/>"
        "<b>Q5 - Governanca AmazonTech:</b> playbooks versionados, baseline de policy, "
        "logging (ScriptBlock), modulos assinados e JEA transformam admin ad-hoc em "
        "processo controlado e auditavel.",
        st["Body"]))

    story.append(Paragraph("7. Dificuldades Encontradas", st["H1"]))
    story.append(Paragraph(
        "A invocacao do script de evidencia com -ExecutionPolicy Bypass elevou o escopo "
        "Process, o que poderia confundir a leitura da politica efetiva; o detalhamento "
        "por escopo (-List) esclareceu que CurrentUser permanece RemoteSigned. "
        "Nenhuma politica permanente foi alterada.",
        st["Body"]))

    story.append(Paragraph("8. Conclusao Tecnica / Parecer", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Estacao", "WIN-ADM-01 / MachadoPC"),
        ("Escopo", "Administracao segura PowerShell (somente consulta)"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "O PowerShell 5.1 esta <b>operacional</b> como plataforma de administracao: ajuda, "
        "inventario de comandos, consultas de SO/servicos e integracao com Defender/Firewall "
        "validados. Fecha o ciclo da Aula 7 (07A–07D) unindo protecao tecnica e governanca "
        "operacional. Recomenda-se baseline corporativa de Execution Policy + logging.<br/>"
        "<b>Parecer:</b> [X] <b>APTO — POWERSHELL VALIDADO COMO PLATAFORMA DE "
        "ADMINISTRACAO SEGURA</b> para consultas e futuros playbooks autorizados.<br/>"
        f"<b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("Checklist Final + Encerramento 07A–07D", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["Ambiente / versao PowerShell documentados", "SIM"],
            ["Get-Help / Get-Command executados", "SIM"],
            ["Get-Service / Get-Process amostrados", "SIM"],
            ["Execution Policy interpretada", "SIM"],
            ["Get-ComputerInfo + integracao 07A/07B", "SIM"],
            ["Questoes de encerramento respondidas", "SIM"],
            ["Nenhuma config permanente alterada", "SIM"],
            ["Ciclo Aula 7 (07A+07B+07C+07D) consolidado", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))
    story.append(Paragraph(
        "Docs: lab07d/evidencias/docs/Notas_Governanca_PowerShell.txt",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 07D - PowerShell + Screenshots"),
              onLaterPages=footer("Lab 07D - PowerShell + Screenshots"))
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
