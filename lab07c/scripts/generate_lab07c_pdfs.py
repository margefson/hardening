#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 07C PDFs: Ordem de Servico + BitLocker."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab07c")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab07C_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab07C_BitLocker_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab07C_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab07C_BitLocker_PREENCHIDO.pdf")

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
    ("02_disponibilidade_bitlocker", "Evidencia 2 - Disponibilidade BitLocker"),
    ("03_tpm", "Evidencia 3 - TPM"),
    ("04_manage_bde_status", "Evidencia 4 - manage-bde -status"),
    ("05_powershell_bitlocker", "Evidencia 5 - Cmdlets BitLocker"),
    ("06_recuperacao", "Evidencia 6 - Chave de recuperacao"),
    ("07_aptidao_hardware", "Evidencia 7 - Aptidao AmazonTech"),
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
        elif "TPM 2.0" in ln or "PRESENTE" in ln or "True" in ln or "OK" in ln:
            color = "#79c0ff"
        elif "negad" in ln.lower() or "AUSENTE" in ln or "False" in ln or "ERRO" in ln or "Home" in ln:
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
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lab 07C")
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
                            title="Lab 07C - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 07C", st["CoverTitle"]))
    story.append(Paragraph("Administracao e Validacao do BitLocker", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        "Status: CONCLUIDA | Somente verificacao (BitLocker NAO habilitado)",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Estacao", "WIN-ADM-01 (MachadoPC)"),
        ("SO", "Microsoft Windows 11 Home Single Language (build 26200)"),
        ("Disciplina", "Criptografia e Trusted Computing / Windows Hardening III"),
        ("Tipo", "Validacao de criptografia de unidades (BitLocker/TPM)"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Resultado", st["H1"]))
    story.append(grid(
        ["Situacao", "Resultado", "Status"],
        [
            ["Disponibilidade BitLocker", "Home: CPL/Wizard ausentes; manage-bde/modulo PS presentes", "Limitado"],
            ["TPM", "Trusted Platform Module 2.0 presente (PnP OK); Get-Tpm exige admin", "Presente"],
            ["Estado das unidades", "C/D/F NTFS Healthy; manage-bde -status exige elevacao", "Parcial"],
            ["Cmdlets BitLocker", "15 funcoes + DeviceEncryption/WizardElev listados", "OK"],
            ["Chave de recuperacao", "Finalidade documentada; nenhuma chave alterada", "Explorado"],
            ["Politica AmazonTech", "Aptidao parcial ate Pro/Enterprise ou Device Encryption", "Avaliado"],
        ],
        st, [4.2*cm, 9.3*cm, 2.7*cm], WARN
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "02_disponibilidade_bitlocker", st))
    story.append(PageBreak())
    story.append(shot(paths, "03_tpm", st))
    story.append(shot(paths, "04_manage_bde_status", st))
    story.append(PageBreak())
    story.append(shot(paths, "05_powershell_bitlocker", st))
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Disponibilidade do BitLocker verificada", "SIM (Home = parcial)"],
            ["2. TPM verificado quando aplicavel", "SIM (TPM 2.0)"],
            ["3. Estado da protecao das unidades analisado", "PARCIAL (sem elevacao)"],
            ["4. Mecanismos administrativos localizados", "SIM"],
            ["5. Funcao da chave de recuperacao compreendida", "SIM"],
            ["6. Evidencias tecnicas registradas", "SIM"],
            ["7. BitLocker NAO habilitado nesta atividade", "SIM"],
            ["8. Limitacoes de edicao/permissao documentadas", "SIM"],
        ],
        st, [13.2*cm, 3.5*cm], WARN
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - auditoria BitLocker/TPM; aptidao parcial (edicao Home)"),
        ("Documento tecnico", "Lab07C_BitLocker_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 07C - Ordem de Servico"),
              onLaterPages=footer("Lab 07C - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 07C - BitLocker", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 07C", st["CoverTitle"]))
    story.append(Paragraph("Administracao e Validacao do BitLocker", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Estacao: WIN-ADM-01",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Equipe", TEAM),
        ("Data", DATE),
        ("Laboratorio", "07C - BitLocker"),
        ("Sistema Operacional", "Microsoft Windows 11 Home Single Language"),
        ("Versao / Build", "10.0.26200 (build 26200)"),
        ("Hostname", "MachadoPC (WIN-ADM-01)"),
    ], st))

    story.append(Paragraph("2. Objetivo", st["H1"]))
    story.append(Paragraph(
        "Validar recursos relacionados ao BitLocker e ao TPM para proteger dados "
        "<b>em repouso</b> nos endpoints Windows da AmazonTech: disponibilidade do recurso, "
        "presenca do TPM, estado das unidades, cmdlets administrativos e chaves de recuperacao "
        "— <b>sem habilitar</b> criptografia nesta Ordem de Servico.",
        st["Body"]))

    story.append(Paragraph("3. Ferramentas Utilizadas", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade"],
        [
            ["Painel BitLocker / Device Encryption", "Disponibilidade UI do recurso"],
            ["tpm.msc / Get-PnpDevice", "Presenca e versao do TPM"],
            ["manage-bde -status", "Estado de protecao das unidades"],
            ["Get-Command *BitLocker*", "Inventario de cmdlets"],
            ["Get-BitLockerVolume", "Status via PowerShell (quando elevado)"],
            ["manage-bde -protectors -get", "Protetores / recuperacao (leitura)"],
            ["Get-Volume", "Inventario de volumes NTFS"],
        ],
        st, [6.2*cm, 10.5*cm]
    ))

    story.append(Paragraph("4. Evidencias Coletadas", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_disponibilidade_bitlocker", st))
    story.append(shot(paths, "03_tpm", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_manage_bde_status", st))
    story.append(shot(paths, "05_powershell_bitlocker", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_recuperacao", st))
    story.append(shot(paths, "07_aptidao_hardware", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("5. Resultados Obtidos", st["H1"]))
    story.append(Paragraph("5.1 Disponibilidade (Atividade 1)", st["H2"]))
    story.append(Paragraph(
        "Edicao <b>Windows 11 Home Single Language</b>: BitLockerCpl.dll e BitLockerWizard "
        "ausentes; manage-bde.exe, fveapi.dll, modulo PowerShell BitLocker e "
        "BitLockerDeviceEncryption.exe presentes. Servico BDESVC = Stopped/Manual. "
        "Conclusao: ferramentas de plataforma existem, mas a UI/experiencia completa de "
        "BitLocker Drive Encryption tipicamente exige Pro/Enterprise; Device Encryption "
        "pode ser caminho em hardware elegivel.",
        st["Body"]))

    story.append(Paragraph("5.2 TPM (Atividade 2)", st["H2"]))
    story.append(Paragraph(
        "tpm.msc presente. Get-Tpm/Win32_Tpm exigiram elevacao. Via PnP: "
        "<b>Trusted Platform Module 2.0</b> com Status OK; servico tpm.sys instalado. "
        "TPM e critico para selar chaves ao estado de boot (PCRs) e permitir desbloqueio "
        "automatico seguro do BitLocker.",
        st["Body"]))

    story.append(Paragraph("5.3 Unidades e PowerShell (Ativ. 3-4)", st["H2"]))
    story.append(Paragraph(
        "Volumes C:/D:/F: NTFS Healthy. manage-bde -status e Get-BitLockerVolume retornaram "
        "acesso negado sem administrador — limitacao registrada conforme a OS. "
        "Get-Command *BitLocker* listou 15 funcoes (Enable/Disable/Get/Suspend/Unlock/"
        "Backup*KeyProtector etc.) + executaveis DeviceEncryption/WizardElev.",
        st["Body"]))

    story.append(Paragraph("5.4 Recuperacao (Atividade 5)", st["H2"]))
    story.append(Paragraph(
        "Chave de recuperacao (48 digitos / backup AD/Entra/USB/conta Microsoft) permite "
        "desbloquear a unidade quando TPM falha, hardware muda ou PIN e esquecido. "
        "Custodia corporativa e obrigatoria antes da ativacao em notebooks externos. "
        "Nenhuma chave foi gerada ou alterada nesta atividade.",
        st["Body"]))

    story.append(Paragraph("6. Questoes de Encerramento", st["H1"]))
    story.append(Paragraph(
        "<b>Q1 - Papel do BitLocker:</b> terceira camada da protecao de endpoints — "
        "confidencialidade dos dados em repouso, mesmo em perda/roubo do notebook/disco.<br/><br/>"
        "<b>Q2 - Suporte ao BitLocker?</b> <b>Parcial</b>. Home nao expoe UI completa; "
        "ferramentas (manage-bde, modulo PS, Device Encryption) estao presentes; politica "
        "obrigatoria plena recomenda Pro/Enterprise.<br/><br/>"
        "<b>Q3 - TPM?</b> <b>Sim — TPM 2.0</b> (PnP OK). Importancia: root of trust para "
        "chaves e integridade de boot.<br/><br/>"
        "<b>Q4 - Limitacoes:</b> edicao Home; manage-bde/Get-Tpm/Get-BitLockerVolume exigem "
        "elevacao; status de criptografia nao lido sem admin; BitLocker nao habilitado "
        "(restricao da OS).<br/><br/>"
        "<b>Q5 - Por que criptografia obrigatoria em notebooks?</b> Colaboradores externos "
        "aumentam risco de perda fisica; sem criptografia, o disco pode ser montado em outro "
        "host e os dados lidos. BitLocker mitiga esse risco residual apos Defender e Firewall.",
        st["Body"]))

    story.append(Paragraph("7. Dificuldades Encontradas", st["H1"]))
    story.append(Paragraph(
        "Windows 11 Home limita a gestao corporativa do BitLocker. Consultas privilegiadas "
        "(Get-Tpm, manage-bde -status, protectors) falharam sem elevacao. A aptidao para a "
        "politica AmazonTech e portanto <b>parcial</b> ate upgrade de edicao ou Device "
        "Encryption homologado com custodia de recovery key.",
        st["Body"]))

    story.append(Paragraph("8. Conclusao Tecnica / Parecer", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Estacao", "WIN-ADM-01 / MachadoPC"),
        ("Escopo", "Validacao BitLocker/TPM (sem habilitar criptografia)"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "A auditoria confirma <b>TPM 2.0</b> e componentes de plataforma BitLocker/Device "
        "Encryption, mas a edicao <b>Home</b> e a falta de elevacao impedem homologar "
        "criptografia completa neste endpoint como notebook corporativo externo. "
        "Complementa Labs 07A (Defender) e 07B (Firewall) na defesa em profundidade — "
        "protecao em execucao, em transito e em repouso.<br/>"
        "<b>Parecer:</b> [X] <b>AUDITORIA CONCLUIDA — APTO COM RESSALVAS</b> "
        "(upgrade Pro/Enterprise ou Device Encryption + elevacao/custodia de chave "
        "antes da politica obrigatoria).<br/>"
        f"<b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("Checklist Final", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["Disponibilidade do BitLocker verificada", "SIM"],
            ["TPM verificado (TPM 2.0)", "SIM"],
            ["Estado das unidades analisado (com limitacao)", "SIM"],
            ["Cmdlets BitLocker inventariados", "SIM"],
            ["Chave de recuperacao compreendida", "SIM"],
            ["Questoes de encerramento respondidas", "SIM"],
            ["BitLocker NAO habilitado nesta OS", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))
    story.append(Paragraph(
        "Docs: lab07c/evidencias/docs/Nota_Chave_Recuperacao_BitLocker.txt",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 07C - BitLocker + Screenshots"),
              onLaterPages=footer("Lab 07C - BitLocker + Screenshots"))
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
