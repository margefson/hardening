#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 06D PDFs: Ordem de Servico + Governanca e Security Baselines."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab06d")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab06D_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab06D_Governanca_Security_Baselines_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab06D_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab06D_Governanca_Security_Baselines_PREENCHIDO.pdf")

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
    ("02_sct_baseline", "Evidencia 2 - Security Compliance Toolkit"),
    ("03_lgpo", "Evidencia 3 - LGPO.exe + politicas locais"),
    ("04_gpedit_mmc", "Evidencia 4 - gpedit / MMC"),
    ("05_sca_compare", "Evidencia 5 - SCA / comparacao baseline"),
    ("06_comparacao_config", "Evidencia 6 - Config atual x baseline"),
    ("07_recomendacoes", "Evidencia 7 - Recomendacoes consolidadas"),
    ("08_plano_governanca", "Evidencia 8 - Plano Corporativo de Governanca"),
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
        elif "EnableLUA" in ln or "ADERENTE" in ln or "Baseline" in ln:
            color = "#79c0ff"
        elif "DIVERGENTE" in ln or "RISCO" in ln or "ausentes" in ln.lower() or "nao instalados" in ln.lower():
            color = "#ff7b72"
        elif ln.startswith("#") or ln.startswith("-"):
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
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lab 06D")
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
                            title="Lab 06D - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 06D", st["CoverTitle"]))
    story.append(Paragraph("Governanca da Arquitetura de Seguranca e Security Baselines", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph("Status: CONCLUIDA | Sem alteracao de politicas (somente avaliacao)", st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Estacao", "WIN-ADM-01 (MachadoPC)"),
        ("SO", "Microsoft Windows 11 Home Single Language (build 26200)"),
        ("Tipo", "Auditoria, validacao e padronizacao das configs de seguranca"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Resultado", st["H1"]))
    story.append(grid(
        ["Situacao", "Resultado", "Status"],
        [
            ["Security Baselines", "SCT analisado; baseline Win11 recomendada; SCT nao instalado no host", "Avaliado"],
            ["Politicas de Seguranca", "UAC ativo; gpedit/secpol ausentes (Home); auditpol amostrado", "Revisado"],
            ["Ferramentas de Governanca", "MMC disponivel; LGPO ausente; SCA conceitual + comparacao", "Identificado"],
            ["Padronizacao", "Drift vs baseline (admin diario, NTFS Auth Users)", "Validado"],
            ["Conformidade", "Parcial — inventarios 06A-C OK; falta baseline aplicada", "Verificado"],
            ["Plano de Governanca", "Plano corporativo elaborado (evidencia 08)", "Consolidado"],
        ],
        st, [4.2*cm, 9.3*cm, 2.7*cm], WARN
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "02_sct_baseline", st))
    story.append(PageBreak())
    story.append(shot(paths, "03_lgpo", st))
    story.append(shot(paths, "05_sca_compare", st))
    story.append(PageBreak())
    story.append(shot(paths, "07_recomendacoes", st))
    story.append(shot(paths, "08_plano_governanca", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Configs seguem Security Baselines aprovadas", "PARCIAL (proposta; nao aplicada)"],
            ["2. Politicas documentadas e revisadas", "SIM (plano + labs 06A-C)"],
            ["3. Alteracoes registradas/auditadas", "SIM (sem alteracao nesta OS)"],
            ["4. Admin centralizada quando possivel", "PARCIAL (MMC; falta GPO/Intune/LGPO)"],
            ["5. Evidencias tecnicas produzidas", "SIM"],
            ["6. Padronizacao e manutencao continua", "SIM (plano)"],
            ["7. Nenhuma config alterada sem autorizacao", "SIM"],
            ["8. Subsidia Plano Corporativo de Governanca", "SIM"],
        ],
        st, [13.2*cm, 3.5*cm], WARN
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - governanca avaliada; Plano Corporativo entregue"),
        ("Documento tecnico", "Lab06D_Governanca_Security_Baselines_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 06D - Ordem de Servico"),
              onLaterPages=footer("Lab 06D - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 06D - Governanca Security Baselines", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 06D", st["CoverTitle"]))
    story.append(Paragraph("Governanca da Arquitetura de Seguranca e Security Baselines", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Estacao: WIN-ADM-01",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Objetivo da Auditoria", st["H1"]))
    story.append(Paragraph(
        "Fechar o ciclo 06A–06C respondendo: como manter a arquitetura padronizada ao longo "
        "do tempo? Avaliar Security Baselines, LGPO, politicas locais, MMC/SCA e elaborar o "
        "<b>Plano Corporativo de Governanca</b>, sem alterar configuracoes nesta estacao.",
        st["Body"]))

    story.append(Paragraph("2. Ferramentas Utilizadas", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade"],
        [
            ["Microsoft Security Compliance Toolkit", "Baselines oficiais e PolicyAnalyzer"],
            ["LGPO.exe", "Exportar/importar/aplicar politicas locais"],
            ["gpedit.msc", "Politicas locais (Enterprise; ausente no Home)"],
            ["MMC", "Centralizar snap-ins de governanca"],
            ["Security Configuration and Analysis", "Comparar host x template/baseline"],
            ["Comparacao de configuracoes", "Mapear aderencias e drifts Labs 06A-C"],
            ["Consolidacao de recomendacoes", "Priorizar acoes de padronizacao"],
            ["Plano Corporativo de Governanca", "Institucionalizar o programa permanente"],
        ],
        st, [6.2*cm, 10.5*cm]
    ))

    story.append(Paragraph("3. Evidencias Produzidas", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_sct_baseline", st))
    story.append(shot(paths, "03_lgpo", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_gpedit_mmc", st))
    story.append(shot(paths, "05_sca_compare", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_comparacao_config", st))
    story.append(shot(paths, "07_recomendacoes", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_plano_governanca", st))

    story.append(Paragraph("4. Resultados Obtidos", st["H1"]))
    story.append(Paragraph("4.1 Security Baselines / SCT (Ex.1)", st["H2"]))
    story.append(Paragraph(
        "Baselines definem um pacote aprovado de settings (Account Policies, User Rights, "
        "Security Options, Firewall, Audit, Admin Templates). SCT nao estava instalado no host "
        "de lab; a analise documental recomenda baseline <b>Windows 11</b> (e Server quando "
        "aplicavel) como referencia AmazonTech. Padronizacao reduz inconsistencias entre admins.",
        st["Body"]))

    story.append(Paragraph("4.2 LGPO / gpedit / MMC (Ex.2–4)", st["H2"]))
    story.append(Paragraph(
        "LGPO automatiza backup/aplicacao de politicas locais — ideal para workgroup/golden image. "
        "gpedit/secpol <b>ausentes</b> no Windows 11 Home; UAC permanece EnableLUA=1. "
        "MMC disponivel para centralizar SCA, Event Viewer e Computer Management. "
        "Automacao evita drift por edicao manual inconsistente.",
        st["Body"]))

    story.append(Paragraph("4.3 SCA e comparacao (Ex.5–6)", st["H2"]))
    story.append(Paragraph(
        "<b>Aderente:</b> UAC on; Guest/Default/Admin built-in desabilitados; auditorias 06A–C "
        "documentadas.<br/>"
        "<b>Divergente:</b> admin permanente na conta diaria; NTFS com Auth Users Modify; "
        "SCT/LGPO ausentes; Security log limitado sem elevacao. Divergencias sao riscos "
        "relevantes de privilegio e need-to-know se nao remediadas sob governanca.",
        st["Body"]))

    story.append(Paragraph("4.4 Plano Corporativo (Ex.7–8)", st["H2"]))
    story.append(Paragraph(
        "Plano inclui objetivo, mecanismos (SCT/LGPO/GPO/Intune), ferramentas, periodicidade "
        "(diario→trimestral), responsaveis e indicadores (% hosts conformes, admin injustificado=0, "
        "ACL sensivel=0). Integra Labs 06A–06D em ciclo permanente.",
        st["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("5. Analise Tecnica", st["H1"]))
    story.append(Paragraph(
        "Hardening pontual sem governanca degrada com o tempo. Baselines + LGPO/GPO transformam "
        "achados dos labs em estado desejado reaplicavel. A edicao Home limita gpedit local, "
        "reforcando a necessidade de imagem corporativa Enterprise/Server ou gestao Intune/GPO "
        "para a frota AmazonTech. Prioridade: instalar SCT, aprovar baseline, remover admin "
        "diario, corrigir ACL Financeiro — tudo via change control.",
        st["Body"]))

    story.append(Paragraph("6. Recomendacoes", st["H1"]))
    story.append(grid(
        ["#", "Recomendacao", "Prioridade"],
        [
            ["1", "Instalar SCT + PolicyAnalyzer; versionar baseline AmazonTech", "Alta"],
            ["2", "Aplicar via LGPO (lab/workgroup) ou GPO/Intune (producao)", "Alta"],
            ["3", "Remediar drifts 06A-C (admin JIT; ACL GRP_*)", "Alta"],
            ["4", "SCA/PolicyAnalyzer mensal; ciclo completo trimestral", "Media"],
            ["5", "Padronizar frota em edicao Enterprise/Server gerenciavel", "Media"],
            ["6", "Indicadores do Plano Corporativo no comite de Seguranca", "Media"],
        ],
        st, [1.2*cm, 12.5*cm, 3.0*cm], WARN
    ))

    story.append(Paragraph("7. Conclusao / Parecer", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Estacao", "WIN-ADM-01 / MachadoPC"),
        ("Escopo", "Governanca e Security Baselines (sem alteracao)"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "O Programa Corporativo Windows (06A–06D) esta <b>concluido em nivel de auditoria e "
        "planejamento</b>. Identidades, privilegios e NTFS foram inventariados; a governanca "
        "define como preservar conformidade via baselines. Implantacao efetiva da baseline "
        "depende de autorizacao e ferramentas SCT/LGPO em janela controlada.<br/>"
        "<b>Parecer:</b> [X] <b>PROGRAMA 06 CONCLUIDO — APTO PARA IMPLANTACAO DO PLANO "
        "DE GOVERNANCA</b> mediante aceite da Diretoria.<br/>"
        f"<b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("Checklist Final + Encerramento 06A–06D", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["SCT / conceito de Security Baseline", "SIM"],
            ["LGPO documentado", "SIM"],
            ["gpedit/MMC avaliados", "SIM"],
            ["SCA / comparacao baseline", "SIM"],
            ["Recomendacoes consolidadas", "SIM"],
            ["Plano Corporativo de Governanca", "SIM"],
            ["Integracao Labs 06A+06B+06C+06D", "SIM"],
            ["Nenhuma politica alterada sem autorizacao", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))
    story.append(Paragraph(
        "Docs: lab06d/evidencias/docs/Plano_Corporativo_Governanca_AmazonTech.txt",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 06D - Governanca + Screenshots"),
              onLaterPages=footer("Lab 06D - Governanca + Screenshots"))
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
