#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 06A PDFs: Ordem de Servico + Auditoria das Identidades Windows."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab06a")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab06A_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab06A_Identidades_Windows_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab06A_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab06A_Identidades_Windows_PREENCHIDO.pdf")

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
    ("02_whoami", "Evidencia 2 - whoami"),
    ("03_whoami_user", "Evidencia 3 - whoami /user (SID)"),
    ("04_whoami_groups", "Evidencia 4 - whoami /groups"),
    ("05_net_user", "Evidencia 5 - net user"),
    ("06_net_localgroup", "Evidencia 6 - net localgroup"),
    ("07_lusrmgr_equiv", "Evidencia 7 - lusrmgr.msc (equiv. PowerShell)"),
    ("08_get_localuser", "Evidencia 8 - Get-LocalUser"),
    ("09_whoami_all", "Evidencia 9 - whoami /all"),
]


def font(size=13, bold=False):
    cands = [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf"]
    if bold:
        cands = [r"C:\Windows\Fonts\consolab.ttf"] + cands
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_terminal(text, title, out_path, max_lines=32):
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
        if ln.startswith("PS>") or ln.startswith("C:\\"):
            color = "#3fb950"
        elif "SID" in ln or "Administradores" in ln or "S-1-5-" in ln:
            color = "#79c0ff"
        elif "Erro" in ln or "False" in ln and "Enabled" in ln:
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
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lab 06A")
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
                            title="Lab 06A - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 06A", st["CoverTitle"]))
    story.append(Paragraph("Auditoria das Identidades do Windows", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph("Status: CONCLUIDA | Auditoria somente leitura (sem alteracoes)", st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Estacao", "WIN-ADM-01 (MachadoPC)"),
        ("SO", "Microsoft Windows 11 (build 26200)"),
        ("Tipo", "Auditoria, validacao e reorganizacao das identidades"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Resultado da auditoria", st["H1"]))
    story.append(grid(
        ["Situacao", "Resultado", "Status"],
        [
            ["Contas locais existentes", "6 contas (2 habilitadas: marge, postgres)", "Verificado"],
            ["Contas administrativas", "Administradores: Administrador + marge", "Identificado"],
            ["Grupos locais", "15 grupos locais (incl. Administradores, Usuarios, OpenSSH)", "Analisado"],
            ["Membros administrativos", "marge no grupo Administradores (uso diario)", "Validado"],
            ["SID principais", "marge = S-1-5-21-...-1001", "Interpretado"],
            ["Tokens de acesso", "whoami /all + UAC (token filtrado / medio)", "Compreendido"],
            ["Evidencias", "lab06a/evidencias + PDFs", "Produzido"],
        ],
        st, [4.8*cm, 8.7*cm, 2.7*cm], OK
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "03_whoami_user", st))
    story.append(shot(paths, "05_net_user", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_net_localgroup", st))
    story.append(shot(paths, "07_lusrmgr_equiv", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Identidades com finalidade definida", "PARCIAL (documentar postgres/marge)"],
            ["2. Contas admin apenas quando justificadas", "REVISAR (marge admin + uso diario)"],
            ["3. Grupos refletem estrutura organizacional", "PARCIAL (sem grupos departamentais ainda)"],
            ["4. Acesso preferencialmente via grupos", "SIM (principio registrado)"],
            ["5. Contas inativas registradas para revisao", "SIM (4 desabilitadas)"],
            ["6. Evidencias tecnicas produzidas", "SIM"],
            ["7. Nenhuma config alterada sem autorizacao", "SIM (somente leitura)"],
            ["8. Recomendacoes subsidiam Lab 06B (privilegios)", "SIM"],
        ],
        st, [13.2*cm, 3.5*cm], WARN
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - auditoria de identidades concluida; melhorias recomendadas"),
        ("Documento tecnico", "Lab06A_Identidades_Windows_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 06A - Ordem de Servico"),
              onLaterPages=footer("Lab 06A - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 06A - Identidades Windows", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 06A", st["CoverTitle"]))
    story.append(Paragraph("Auditoria das Identidades do Windows", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Estacao: WIN-ADM-01 (MachadoPC)",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Objetivo da Auditoria", st["H1"]))
    story.append(Paragraph(
        "Identificar quem sao as identidades no ambiente Windows da AmazonTech (WIN-ADM-01), "
        "avaliar se refletem a organizacao esperada e produzir evidencias sem alterar "
        "configuracoes. A auditoria e pre-requisito para a revisao de privilegios (Lab 06B), "
        "pois nenhuma autorizacao e confiavel se o sistema nao souber com precisao quem solicita acesso.",
        st["Body"]))

    story.append(Paragraph("2. Ferramentas Utilizadas", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade"],
        [
            ["whoami", "Identificar conta autenticada na sessao"],
            ["whoami /user", "Exibir SID da identidade autenticada"],
            ["whoami /groups", "Listar grupos presentes no Access Token"],
            ["net user", "Inventariar e detalhar contas locais"],
            ["net localgroup", "Listar grupos locais e membros (Administradores)"],
            ["lusrmgr.msc (equiv. Get-Local*)", "Visao consolidada grafica/administrativa"],
            ["Get-LocalUser", "Auditoria automatizada via PowerShell"],
            ["whoami /all", "Visao consolidada (SID, grupos, privilegios/token)"],
        ],
        st, [5.5*cm, 11.2*cm]
    ))

    story.append(Paragraph("3. Evidencias Produzidas", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_whoami", st))
    story.append(shot(paths, "03_whoami_user", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_whoami_groups", st))
    story.append(PageBreak())
    story.append(shot(paths, "05_net_user", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_net_localgroup", st))
    story.append(shot(paths, "07_lusrmgr_equiv", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_get_localuser", st))
    story.append(shot(paths, "09_whoami_all", st))

    story.append(Paragraph("4. Resultados Obtidos", st["H1"]))
    story.append(Paragraph("4.1 Ambiente e identidade autenticada", st["H2"]))
    story.append(Paragraph(
        "<b>Ex.1 whoami:</b> autenticado <b>machadopc\\marge</b> (conta <b>local</b>, nao dominio). "
        "Corresponde ao operador do laboratorio. Sem identidade correta, o Windows nao aplica "
        "autorizacao de forma confiavel.<br/>"
        "<b>Ex.2 whoami /user:</b> SID <b>S-1-5-21-2273054947-3814652866-1034022874-1001</b>. "
        "Pertence a marge. O Windows usa SID (nao o nome) nas ACLs; renomear a conta nao muda o SID.",
        st["Body"]))

    story.append(Paragraph("4.2 Grupos e token", st["H2"]))
    story.append(Paragraph(
        "<b>Ex.3 whoami /groups:</b> multiplos grupos no token (BUILTIN\\Usuarios, Usuarios autenticados, "
        "MicrosoftAccount\\margefson@outlook.com, etc.). BUILTIN\\Administradores aparece com atributo "
        "de negacao (token filtrado UAC / integridade media) — sessao interativa nao eleva "
        "automaticamente todos os privilegios admin.<br/>"
        "<b>Discussao:</b> permissoes via grupos sao mais eficientes e auditaveis do que ACLs por usuario.",
        st["Body"]))

    story.append(Paragraph("4.3 Inventario de contas e grupos", st["H2"]))
    story.append(grid(
        ["Conta", "Estado", "Observacao"],
        [
            ["Administrador", "Desabilitada", "Conta built-in; membro de Administradores"],
            ["Convidado", "Desabilitada", "Built-in; manter desabilitada"],
            ["DefaultAccount", "Desabilitada", "Conta de sistema"],
            ["marge", "Habilitada", "Operador diario; membro de Administradores"],
            ["postgres", "Habilitada", "Conta de servico PostgreSQL — documentar finalidade"],
            ["WDAGUtilityAccount", "Desabilitada", "Windows Defender Application Guard"],
        ],
        st, [4.0*cm, 2.8*cm, 9.9*cm]
    ))
    story.append(Paragraph(
        "<b>Ex.4 net user:</b> 6 contas locais. Contas built-in inativas OK. Contas a investigar: "
        "<b>postgres</b> (servico) e <b>marge</b> (admin + uso diario).<br/>"
        "<b>Ex.5 net localgroup:</b> 15 grupos. Criticos: Administradores (Administrador, marge), "
        "Usuarios, OpenSSH, IIS_IUSRS, Hyper-V.<br/>"
        "<b>Ex.6 lusrmgr equiv.:</b> mesma visao consolidada; GUI facilita revisao, PowerShell "
        "facilita auditoria em escala.<br/>"
        "<b>Ex.7 Get-LocalUser:</b> confirma Enabled/Disabled e SIDs; ideal para automacao.<br/>"
        "<b>Ex.8 whoami /all:</b> consolida identidade, SID, grupos e privilegios do token.",
        st["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("5. Analise Tecnica", st["H1"]))
    story.append(Paragraph(
        "A infraestrutura <b>nao esta plenamente alinhada</b> a uma organizacao corporativa madura, "
        "mas oferece base auditavel para o Lab 06B.<br/>"
        "<b>Pontos positivos:</b> Contas Guest/Default/WDAG desabilitadas; Administrador built-in "
        "desabilitado; inventario completo obtido sem alteracoes; evidencia de UAC (token filtrado).<br/>"
        "<b>Oportunidades:</b> (1) conta de uso diario no grupo Administradores viola menor privilegio; "
        "(2) ausencia de grupos departamentais (TI, Financeiro, etc.); (3) conta postgres habilitada "
        "sem descricao corporativa formal; (4) Microsoft Account vinculada exige politica clara de "
        "identidade cloud vs local.<br/>"
        "<b>Discussao remocao de contas:</b> nao remover imediatamente contas sem uso — risco de "
        "quebrar servicos/ACL. Registrar, desabilitar apos validacao e so entao remover com change control.",
        st["Body"]))

    story.append(Paragraph("6. Recomendacoes", st["H1"]))
    story.append(grid(
        ["#", "Recomendacao", "Prioridade"],
        [
            ["1", "Separar conta diaria de conta admin nominativa (JIT/UAC)", "Alta"],
            ["2", "Documentar finalidade de postgres (servico) e restringir logon interativo", "Alta"],
            ["3", "Criar grupos organizacionais e conceder acesso via grupos", "Media"],
            ["4", "Manter Guest/Default desabilitados; revisar membros de Administradores", "Media"],
            ["5", "Automatizar inventario periodico com Get-LocalUser/Get-LocalGroup", "Media"],
            ["6", "Levar achados ao Lab 06B (auditoria de privilegios)", "Alta"],
        ],
        st, [1.2*cm, 12.5*cm, 3.0*cm], WARN
    ))

    story.append(Paragraph("7. Conclusao / Parecer", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Estacao", "WIN-ADM-01 / MachadoPC"),
        ("Escopo", "Auditoria de identidades (sem alteracao)"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "A organizacao atual das identidades <b>oferece base adequada para a proxima etapa</b> "
        "(Lab 06B — privilegios), desde que as recomendacoes de segregacao admin/diario e "
        "documentacao de contas de servico sejam encaminhadas. A auditoria respondeu a pergunta "
        "da OS: as identidades foram inventariadas, SIDs/tokens compreendidos e inconsistencias "
        "registradas com evidencias.<br/>"
        "<b>Parecer:</b> [X] <b>AUDITORIA CONCLUIDA — APTO PARA AVANCAR AO LAB 06B</b> com plano "
        f"de reorganizacao de identidades.<br/><b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("Checklist Final", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["whoami / whoami /user / groups / all", "SIM"],
            ["net user + detalhe de contas", "SIM"],
            ["net localgroup + Administradores", "SIM"],
            ["lusrmgr.msc / Get-Local* equivalente", "SIM"],
            ["Get-LocalUser", "SIM"],
            ["SID e Access Token interpretados", "SIM"],
            ["Recomendacoes + evidencias + parecer", "SIM"],
            ["Nenhuma configuracao alterada", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))
    story.append(Paragraph(
        "Screenshots: lab06a/evidencias/shots/img/ | Scripts: lab06a/scripts/",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 06A - Identidades Windows + Screenshots"),
              onLaterPages=footer("Lab 06A - Identidades Windows + Screenshots"))
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
