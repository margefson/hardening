#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 06C PDFs: Ordem de Servico + Auditoria das Permissoes NTFS."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab06c")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab06C_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab06C_Permissoes_NTFS_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab06C_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab06C_Permissoes_NTFS_PREENCHIDO.pdf")

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
    ("01_ambiente", "Evidencia 1 - Ambiente e arvore AmazonTech"),
    ("02_explorer_security_equiv", "Evidencia 2 - Guia Seguranca (equiv.)"),
    ("03_advanced_acl", "Evidencia 3 - ACL avancada / heranca"),
    ("04_effective_access", "Evidencia 4 - Effective Access (equiv.)"),
    ("05_icacls", "Evidencia 5 - icacls"),
    ("06_get_acl", "Evidencia 6 - Get-Acl"),
    ("07_get_childitem", "Evidencia 7 - Get-ChildItem inventario"),
    ("08_comparacao", "Evidencia 8 - Comparacao GUI vs CLI"),
    ("09_consolidacao", "Evidencia 9 - Consolidacao da auditoria"),
]


def font(size=12, bold=False):
    cands = [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf"]
    if bold:
        cands = [r"C:\Windows\Fonts\consolab.ttf"] + cands
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_terminal(text, title, out_path, max_lines=34):
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
        if ln.startswith("PS>") or ln.startswith("===") or ln.startswith("====="):
            color = "#3fb950"
        elif "FullControl" in ln or "(F)" in ln or "Modify" in ln or "(M)" in ln:
            color = "#79c0ff"
        elif "Usuarios autenticados" in ln or "need-to-know" in ln or "risco" in ln.lower():
            color = "#ff7b72"
        elif ln.startswith("#"):
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
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lab 06C")
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
    if th > 8.2*cm:
        th = 8.2*cm
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
                            title="Lab 06C - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 06C", st["CoverTitle"]))
    story.append(Paragraph("Auditoria das Permissoes NTFS", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph("Status: CONCLUIDA | Auditoria somente leitura (ACL nao alteradas)", st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Estacao", "WIN-ADM-01 (MachadoPC)"),
        ("SO", "Microsoft Windows 11 (build 26200)"),
        ("Tipo", "Auditoria e reorganizacao das permissoes de acesso"),
        ("Escopo auditado", "ambiente_simulado\\AmazonTech (Financeiro, Projetos, Auditoria, TI, Compartilhado)"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Resultado", st["H1"]))
    story.append(grid(
        ["Situacao", "Resultado", "Status"],
        [
            ["Permissoes NTFS", "ACL padrao herdada; Authenticated Users=Modify em pastas", "Verificado"],
            ["ACL / DACL", "8 ACE tipicas (Admins, SYSTEM, Auth Users, Users)", "Analisado"],
            ["Heranca", "Ativa (AreAccessRulesProtected=False; IsInherited=True)", "Validado"],
            ["Permissoes efetivas", "Sessao marge: leitura/escrita efetiva na arvore lab", "Revisado"],
            ["Recursos compartilhados", "Financeiro ~ mesmo perfil de Compartilhado (falta segregacao)", "Avaliado"],
            ["Evidencias", "lab06c/evidencias + PDFs", "Produzido"],
        ],
        st, [4.2*cm, 9.3*cm, 2.7*cm], WARN
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "02_explorer_security_equiv", st))
    story.append(PageBreak())
    story.append(shot(paths, "05_icacls", st))
    story.append(shot(paths, "06_get_acl", st))
    story.append(PageBreak())
    story.append(shot(paths, "07_get_childitem", st))
    story.append(shot(paths, "09_consolidacao", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Permissoes preferencialmente via grupos", "PARCIAL (grupos built-in amplos)"],
            ["2. Acesso apenas ao necessario (need-to-know)", "NAO (Financeiro aberto a Auth Users)"],
            ["3. Heranca consistente e documentada", "SIM (heranca ativa; falta documentacao formal)"],
            ["4. Alteracoes so com autorizacao", "SIM (nenhuma ACL alterada)"],
            ["5. Evidencias tecnicas produzidas", "SIM"],
            ["6. Recomendacoes protegem informacoes", "SIM"],
            ["7. Nenhuma config alterada sem autorizacao", "SIM"],
            ["8. Subsidia Governanca / Security Baselines", "SIM"],
        ],
        st, [13.2*cm, 3.5*cm], WARN
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - NTFS auditado; reorganizacao de ACL recomendada"),
        ("Documento tecnico", "Lab06C_Permissoes_NTFS_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 06C - Ordem de Servico"),
              onLaterPages=footer("Lab 06C - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 06C - Permissoes NTFS", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 06C", st["CoverTitle"]))
    story.append(Paragraph("Auditoria das Permissoes NTFS", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Estacao: WIN-ADM-01 (MachadoPC)",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Objetivo da Auditoria", st["H1"]))
    story.append(Paragraph(
        "Apos identidades (06A) e privilegios (06B), auditar <b>quais recursos</b> cada identidade "
        "pode acessar via NTFS — ACL/DACL, heranca e permissoes efetivas — sem alterar ACL. "
        "Pergunta da OS: as permissoes garantem acesso apenas ao necessario para a funcao?",
        st["Body"]))

    story.append(Paragraph("2. Ferramentas Utilizadas", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade"],
        [
            ["Explorer > Seguranca (equiv. Get-Acl)", "Permissoes NTFS basicas"],
            ["Seguranca Avancada (equiv.)", "Owner, ACL, heranca, ACE explicitas/herdadas"],
            ["Effective Access (equiv.)", "Permissao efetiva por identidade"],
            ["icacls", "Consulta NTFS via CMD"],
            ["Get-Acl", "ACL via PowerShell"],
            ["Get-ChildItem", "Inventario de recursos"],
            ["Comparacao GUI x CLI", "Consistencia das evidencias"],
            ["Consolidacao", "Sintese e recomendacoes"],
        ],
        st, [6.0*cm, 10.7*cm]
    ))

    story.append(Paragraph("3. Evidencias Produzidas", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_explorer_security_equiv", st))
    story.append(shot(paths, "03_advanced_acl", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_effective_access", st))
    story.append(shot(paths, "05_icacls", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_get_acl", st))
    story.append(shot(paths, "07_get_childitem", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_comparacao", st))
    story.append(shot(paths, "09_consolidacao", st))

    story.append(Paragraph("4. Resultados Obtidos", st["H1"]))
    story.append(Paragraph("4.1 Inventario e guia Seguranca (Ex.1 / Ex.6)", st["H2"]))
    story.append(Paragraph(
        "Arvore simulada: Financeiro, Projetos, Auditoria, TI, Compartilhado (+ arquivos amostra). "
        "Prioridade: <b>Financeiro</b> (confidencialidade).<br/>"
        "<b>Financeiro — Owner:</b> MACHADOPC\\marge. Identidades na ACL: Administradores (F), "
        "SYSTEM (F), Usuarios autenticados (M), Usuarios (RX). Sem Deny observado. "
        "Permissoes diretas a usuarios individuais: nao; uso de grupos built-in (bom principio, "
        "mas grupos genericos demais para need-to-know).",
        st["Body"]))

    story.append(Paragraph("4.2 ACL avancada e heranca (Ex.2)", st["H2"]))
    story.append(Paragraph(
        "AreAccessRulesProtected=False; ACE com IsInherited=True — heranca ativa do pai. "
        "Entradas OI/CI no icacls confirmam propagacao a arquivos/subpastas. "
        "Heranca facilita administracao, mas propaga tambem excesso de acesso se o pai for permissivo.",
        st["Body"]))

    story.append(Paragraph("4.3 Effective Access (Ex.3)", st["H2"]))
    story.append(Paragraph(
        "Para marge (Users + Administradores, token filtrado): leitura do relatorio financeiro "
        "bem-sucedida; Auth Users=Modify implica gravacao efetiva tipica. Analisar so a ACL "
        "sem Effective Access pode omitir Deny/grupos — Effective Access consolida o resultado final.",
        st["Body"]))

    story.append(Paragraph("4.4 icacls / Get-Acl / Comparacao (Ex.4–5 / Ex.7)", st["H2"]))
    story.append(Paragraph(
        "icacls e Get-Acl sao <b>consistentes</b> com a visao de Seguranca: mesmas identidades e "
        "niveis (F/M/RX). icacls compacto e scriptavel; Get-Acl detalha InheritanceFlags; GUI "
        "Effective Access e melhor para troubleshooting pontual. Para auditoria em escala: "
        "<b>icacls + Get-Acl</b>.",
        st["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("5. Analise Tecnica", st["H1"]))
    story.append(Paragraph(
        "As permissoes <b>nao garantem</b> need-to-know corporativo: pasta Financeiro herda "
        "Modify para Usuarios autenticados — qualquer conta autenticada no host pode alterar "
        "conteudo financeiro do laboratorio. Financeiro e Compartilhado compartilham perfil ACL "
        "semelhante (falta segregacao). Nao ha grupos departamentais (ex.: GRP_FINANCEIRO).<br/>"
        "<b>Discussao:</b> ACE em usuarios individuais dificulta gestao; grupos sao preferiveis, "
        "desde que sejam grupos de funcao (nao apenas Users/Auth Users).",
        st["Body"]))

    story.append(Paragraph("6. Recomendacoes", st["H1"]))
    story.append(grid(
        ["#", "Recomendacao", "Prioridade"],
        [
            ["1", "Criar grupos GRP_FINANCEIRO / GRP_TI / GRP_AUDITORIA e conceder via grupos", "Alta"],
            ["2", "Remover/restringir Auth Users e Users em pastas sensiveis (apos autorizacao)", "Alta"],
            ["3", "Documentar heranca; quebrar heranca so com justificativa e ACE explicitas", "Media"],
            ["4", "Validar Effective Access por persona (DBA, analista, auditor)", "Alta"],
            ["5", "Automatizar inventario Get-ChildItem + Get-Acl/icacls periodico", "Media"],
            ["6", "Nao alterar ACL em producao sem change control / janela", "Alta"],
            ["7", "Seguir para Governanca / Security Baselines", "Alta"],
        ],
        st, [1.2*cm, 12.5*cm, 3.0*cm], WARN
    ))

    story.append(Paragraph("7. Conclusao / Parecer", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Estacao", "WIN-ADM-01 / MachadoPC"),
        ("Escopo", "Auditoria NTFS (ACL nao alteradas)"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "Menor privilegio e need-to-know <b>nao estao adequadamente aplicados</b> nas pastas "
        "simuladas com heranca permissiva de Auth Users. A auditoria documentou ACL, heranca, "
        "permissoes efetivas e consistencia GUI/CLI, com recomendacoes claras sem modificar ACL "
        "(conforme OS).<br/>"
        "<b>Parecer:</b> [X] <b>AUDITORIA CONCLUIDA — APTO PARA ETAPA DE GOVERNANCA / "
        "SECURITY BASELINES</b>, condicionada a reorganizacao das ACL em janela autorizada.<br/>"
        f"<b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("Checklist Final", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["Guia Seguranca / Get-Acl basico", "SIM"],
            ["ACL avancada / owner / heranca", "SIM"],
            ["Effective Access documentado", "SIM"],
            ["icacls", "SIM"],
            ["Get-Acl detalhado", "SIM"],
            ["Get-ChildItem inventario", "SIM"],
            ["Comparacao GUI x CLI", "SIM"],
            ["Consolidacao + recomendacoes + parecer", "SIM"],
            ["Nenhuma ACL alterada", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))
    story.append(Paragraph(
        "Ambiente simulado: lab06c/ambiente_simulado/AmazonTech | Scripts: lab06c/scripts/",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 06C - Permissoes NTFS + Screenshots"),
              onLaterPages=footer("Lab 06C - Permissoes NTFS + Screenshots"))
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
