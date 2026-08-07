#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 07A PDFs: Ordem de Servico + Microsoft Defender."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab07a")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab07A_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab07A_Microsoft_Defender_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab07A_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab07A_Microsoft_Defender_PREENCHIDO.pdf")

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
    ("02_windows_security", "Evidencia 2 - Windows Security / servicos"),
    ("03_estado_protecao", "Evidencia 3 - Estado da protecao"),
    ("04_atualizacoes", "Evidencia 4 - Inteligencia de seguranca"),
    ("05_analise_rapida", "Evidencia 5 - Analise rapida"),
    ("06_historico", "Evidencia 6 - Historico de protecao"),
    ("07_mpcomputerstatus", "Evidencia 7 - Get-MpComputerStatus"),
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
        elif "True" in ln or "Enabled" in ln or "OK" in ln or "ATENDE" in ln:
            color = "#79c0ff"
        elif "False" in ln or "Erro" in ln or "ressalvas" in ln.lower() or "Backdoor" in ln or "Trojan" in ln:
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
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lab 07A")
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
                            title="Lab 07A - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 07A", st["CoverTitle"]))
    story.append(Paragraph("Implantacao e Validacao do Microsoft Defender", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        "Status: CONCLUIDA | Verificacoes e consultas (sem alteracao permanente)",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Estacao", "WIN-ADM-01 (MachadoPC)"),
        ("SO", "Microsoft Windows 11 Home Single Language (build 26200)"),
        ("Disciplina", "Criptografia e Trusted Computing / Windows Hardening III"),
        ("Tipo", "Validacao da protecao de endpoints (Microsoft Defender)"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Resultado", st["H1"]))
    story.append(grid(
        ["Situacao", "Resultado", "Status"],
        [
            ["Windows Security", "App/servicos ativos (WinDefend, MdCoreSvc)", "Validado"],
            ["Protecao em tempo real", "Habilitada (RTP/IOAV/Behavior/NIS)", "OK"],
            ["Nuvem / amostras", "MAPS=2; SubmitSamplesConsent=1; Tamper=True", "OK"],
            ["Assinaturas", "Atualizadas (1.457.40.0; idade 0 dias)", "OK"],
            ["Analise rapida", "QuickScan ~373s; sem erro do cmdlet", "Executado"],
            ["Historico", "Deteccoes passadas tratadas; sem ameaca ativa", "Revisado"],
        ],
        st, [4.2*cm, 9.3*cm, 2.7*cm], OK
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "03_estado_protecao", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_atualizacoes", st))
    story.append(shot(paths, "05_analise_rapida", st))
    story.append(PageBreak())
    story.append(shot(paths, "07_mpcomputerstatus", st))
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Microsoft Defender habilitado no endpoint", "SIM"],
            ["2. Protecao em tempo real operacional", "SIM"],
            ["3. Inteligencia de seguranca atualizada", "SIM"],
            ["4. Analise de sistema executada/documentada", "SIM"],
            ["5. Historico de protecao revisado", "SIM"],
            ["6. Evidencias tecnicas (GUI equiv. + PowerShell)", "SIM"],
            ["7. Sem alteracao permanente de configs criticas", "SIM"],
            ["8. Subsidiou homologacao da camada Defender", "SIM"],
        ],
        st, [13.2*cm, 3.5*cm], OK
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - endpoint apto na camada Microsoft Defender"),
        ("Documento tecnico", "Lab07A_Microsoft_Defender_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 07A - Ordem de Servico"),
              onLaterPages=footer("Lab 07A - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 07A - Microsoft Defender", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 07A", st["CoverTitle"]))
    story.append(Paragraph("Implantacao e Validacao do Microsoft Defender", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Estacao: WIN-ADM-01",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Equipe", TEAM),
        ("Data", DATE),
        ("Laboratorio", "07A - Microsoft Defender"),
        ("Sistema Operacional", "Microsoft Windows 11 Home Single Language"),
        ("Versao / Build", "10.0.26200 (build 26200)"),
        ("Hostname", "MachadoPC (WIN-ADM-01)"),
    ], st))

    story.append(Paragraph("2. Objetivo", st["H1"]))
    story.append(Paragraph(
        "Validar a configuracao do Microsoft Defender como <b>primeira camada</b> da arquitetura "
        "de protecao de endpoints Windows da AmazonTech: localizar Windows Security, verificar "
        "estado da protecao, assinaturas, analise rapida, historico e indicadores via PowerShell "
        "(Get-MpComputerStatus), sem alterar permanentemente configuracoes criticas.",
        st["Body"]))

    story.append(Paragraph("3. Ferramentas Utilizadas", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade"],
        [
            ["Windows Security", "Interface administrativa do Defender"],
            ["Servicos (WinDefend/MdCoreSvc)", "Confirmar motor antimalware ativo"],
            ["Get-MpPreference", "Preferencias (RTP, MAPS, amostras, PUA)"],
            ["Get-MpComputerStatus", "Estado operacional e assinaturas"],
            ["Update-MpSignature", "Verificar atualizacao de inteligencia"],
            ["Start-MpScan (QuickScan)", "Analise rapida do sistema"],
            ["Get-MpThreatDetection / Get-MpThreat", "Historico e ameacas conhecidas"],
        ],
        st, [6.2*cm, 10.5*cm]
    ))

    story.append(Paragraph("4. Evidencias Coletadas", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_windows_security", st))
    story.append(shot(paths, "03_estado_protecao", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_atualizacoes", st))
    story.append(shot(paths, "05_analise_rapida", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_historico", st))
    story.append(shot(paths, "07_mpcomputerstatus", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_consolidacao", st))

    story.append(Paragraph("5. Resultados Obtidos", st["H1"]))
    story.append(Paragraph("5.1 Windows Security e servicos (Ativ. 1)", st["H2"]))
    story.append(Paragraph(
        "A plataforma Windows Security esta disponivel (SecurityHealthSystray presente). "
        "Servicos <b>WinDefend</b> e <b>MdCoreSvc</b> em Running/Automatic; Security Center "
        "registra produto <b>Windows Defender</b> (productState 397568). Modulos esperados: "
        "virus/ameacas, conta, firewall, apps/navegador, dispositivo, saude e familia.",
        st["Body"]))

    story.append(Paragraph("5.2 Estado da protecao (Ativ. 2)", st["H2"]))
    story.append(Paragraph(
        "<b>Habilitados:</b> Antivirus, AMService, Real-Time Protection, IOAV, Behavior Monitor, "
        "On-Access, NIS, Tamper Protection, Controlled Folder Access, PUAProtection.<br/>"
        "<b>Nuvem:</b> MAPSReporting=2 (Advanced); SubmitSamplesConsent=1.<br/>"
        "<b>Desabilitados / risco:</b> DisableRealtimeMonitoring=False (RTP nao desligado). "
        "CloudBlockLevel=0 (padrao; pode-se elevar em politica corporativa).",
        st["Body"]))

    story.append(Paragraph("5.3 Assinaturas e analise (Ativ. 3-4)", st["H2"]))
    story.append(Paragraph(
        "Assinatura atualizada de 1.457.34.0 para <b>1.457.40.0</b> apos Update-MpSignature "
        "(idade 0 dias). QuickScan concluido em ~373 s sem erro; QuickScanAge=0. FullScanAge "
        "elevado (nunca/full antigo) — recomenda-se FullScan periodico em janela autorizada. "
        "Tipos identificados: rapida, completa, personalizada e Defender Offline.",
        st["Body"]))

    story.append(Paragraph("5.4 Historico e PowerShell (Ativ. 5-6)", st["H2"]))
    story.append(Paragraph(
        "Historico contem deteccoes anteriores (ex.: PUABundler/Rostpay, AsyncRAT, Powdow, "
        "ValleyRat, ClipBanker) com ActionSuccess=True e IsActive=False — evidência de resposta "
        "efetiva. Get-MpComputerStatus confirma AMServiceEnabled, AntivirusEnabled, "
        "RealTimeProtectionEnabled, AntivirusSignatureVersion e NISEnabled.",
        st["Body"]))

    story.append(Paragraph("6. Questoes de Encerramento", st["H1"]))
    story.append(Paragraph(
        "<b>Q1 - Papel do Defender:</b> primeira camada de prevencao/deteccao/resposta no endpoint, "
        "complementando identidades, privilegios, NTFS e baselines (Aula 6) na defesa em profundidade.<br/><br/>"
        "<b>Q2 - Mecanismos habilitados:</b> AV, RTP, IOAV, Behavior, NIS, Tamper Protection, "
        "Controlled Folder Access, PUA, MAPS Advanced e envio de amostras.<br/><br/>"
        "<b>Q3 - Atende necessidades basicas?</b> <b>SIM</b>. Motor ativo, RTP on, assinaturas "
        "atuais, scan executado e historico com ameacas tratadas.<br/><br/>"
        "<b>Q4 - Limitacoes:</b> edicao Home (menos gestao centralizada); evidencias via PowerShell "
        "em vez de captura GUI; Sense (MDE) ausente/nao listado; FullScan nao executado nesta OS; "
        "CloudBlockLevel ainda no padrao 0.<br/><br/>"
        "<b>Q5 - Recomendacoes:</b> padronizar preferencias via Intune/GPO; elevar CloudBlockLevel; "
        "FullScan periodico; integrar Microsoft Defender for Endpoint (Sense) na frota; "
        "monitorar historico e ASR/Firewall nos proximos labs.",
        st["Body"]))

    story.append(Paragraph("7. Dificuldades Encontradas", st["H1"]))
    story.append(Paragraph(
        "Windows 11 Home limita administracao corporativa centralizada. Capturas equivalentes "
        "foram obtidas por cmdlets oficiais (mesmo estado da GUI). QuickScan consumiu ~6 min. "
        "Nenhuma configuracao critica permanente foi alterada (restricao da OS).",
        st["Body"]))

    story.append(Paragraph("8. Conclusao Tecnica / Parecer", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Estacao", "WIN-ADM-01 / MachadoPC"),
        ("Escopo", "Validacao Microsoft Defender (sem mudanca permanente)"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "O endpoint apresenta <b>conformidade basica</b> na camada Microsoft Defender: servicos "
        "ativos, protecao em tempo real, Tamper Protection, assinaturas atualizadas e analise "
        "rapida concluida. O historico demonstra capacidade de detectar e tratar ameacas. "
        "Esta e apenas a primeira camada; firewall, criptografia, ASR e administracao reforcada "
        "complementam a arquitetura nas proximas etapas.<br/>"
        "<b>Parecer:</b> [X] <b>APTO PARA HOMOLOGACAO DA CAMADA MICROSOFT DEFENDER</b> "
        "neste endpoint, com recomendacoes de padronizacao corporativa.<br/>"
        f"<b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("Checklist Final", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["Windows Security / servicos identificados", "SIM"],
            ["Estado da protecao documentado", "SIM"],
            ["Assinaturas verificadas/atualizadas", "SIM"],
            ["Analise rapida executada", "SIM"],
            ["Historico de protecao revisado", "SIM"],
            ["Get-MpComputerStatus documentado", "SIM"],
            ["Questoes de encerramento respondidas", "SIM"],
            ["Sem alteracao permanente de configs criticas", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))

    doc.build(story, onFirstPage=footer("Lab 07A - Microsoft Defender + Screenshots"),
              onLaterPages=footer("Lab 07A - Microsoft Defender + Screenshots"))
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
