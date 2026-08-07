#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 06B PDFs: Ordem de Servico + Auditoria dos Privilegios Administrativos."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab06b")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab06B_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab06B_Privilegios_Administrativos_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab06B_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab06B_Privilegios_Administrativos_PREENCHIDO.pdf")

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
    ("02_whoami_priv", "Evidencia 2 - whoami /priv"),
    ("03_user_rights_secedit", "Evidencia 3 - User Rights (secpol/secedit)"),
    ("04_gpedit_status", "Evidencia 4 - gpedit/secpol + UAC"),
    ("05_whoami_all", "Evidencia 5 - whoami /all"),
    ("06_powershell_security", "Evidencia 6 - PowerShell + Administradores"),
    ("07_mmc_equiv", "Evidencia 7 - MMC (paths/snap-ins)"),
    ("08_event_viewer", "Evidencia 8 - Event Viewer / Get-WinEvent"),
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
        if ln.startswith("PS>") or ln.startswith("==="):
            color = "#3fb950"
        elif "Ativada" in ln or "EnableLUA" in ln or "SeChangeNotify" in ln:
            color = "#79c0ff"
        elif "Desativado" in ln or "permissoes" in ln.lower() or "AUSENTES" in ln or "bloqueado" in ln.lower():
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
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lab 06B")
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
                            title="Lab 06B - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 06B", st["CoverTitle"]))
    story.append(Paragraph("Auditoria dos Privilegios Administrativos", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph("Status: CONCLUIDA | Auditoria somente leitura (sem alteracoes)", st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Estacao", "WIN-ADM-01 (MachadoPC)"),
        ("SO", "Microsoft Windows 11 Home Single Language (build 26200)"),
        ("Tipo", "Auditoria e reorganizacao dos privilegios administrativos"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Resultado", st["H1"]))
    story.append(grid(
        ["Situacao", "Resultado", "Status"],
        [
            ["Direitos administrativos", "marge e Administrador no grupo Administradores", "Verificado"],
            ["User Rights Assignment", "secpol ausente (Home); secedit exige elevacao", "Analisado"],
            ["Privilegios no Access Token", "5 listados; 1 Ativada (SeChangeNotifyPrivilege)", "Validado"],
            ["Contas administrativas", "Uso diario com admin (menor privilegio fragil)", "Revisado"],
            ["Menor privilegio", "PARCIAL — UAC ativo, mas admin permanente", "Avaliado"],
            ["Evidencias", "lab06b/evidencias + PDFs", "Produzido"],
        ],
        st, [4.5*cm, 9.0*cm, 2.7*cm], WARN
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "02_whoami_priv", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_gpedit_status", st))
    story.append(shot(paths, "06_powershell_security", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_event_viewer", st))
    story.append(shot(paths, "09_consolidacao", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Todo privilegio com justificativa operacional", "REVISAR"],
            ["2. Principio do menor privilegio nas recomendacoes", "SIM"],
            ["3. Direitos admin apenas quando estritamente necessarios", "REVISAR (marge)"],
            ["4. Alteracoes de politica so com autorizacao", "SIM (nenhuma alteracao)"],
            ["5. Evidencias tecnicas produzidas", "SIM"],
            ["6. Recomendacoes reduzem superficie de ataque", "SIM"],
            ["7. Nenhuma config alterada sem autorizacao", "SIM"],
            ["8. Subsidia proxima etapa (permissoes NTFS)", "SIM"],
        ],
        st, [13.2*cm, 3.5*cm], WARN
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - privilegios auditados; reorganizacao recomendada"),
        ("Documento tecnico", "Lab06B_Privilegios_Administrativos_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 06B - Ordem de Servico"),
              onLaterPages=footer("Lab 06B - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 06B - Privilegios Administrativos", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 06B", st["CoverTitle"]))
    story.append(Paragraph("Auditoria dos Privilegios Administrativos", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Estacao: WIN-ADM-01 (MachadoPC)",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Objetivo da Auditoria", st["H1"]))
    story.append(Paragraph(
        "Apos inventariar identidades (Lab 06A), auditar <b>quais acoes</b> cada identidade "
        "pode executar no Windows — privilegios administrativos, User Rights Assignment e "
        "conteudo do Access Token — avaliando conformidade com o principio do menor privilegio, "
        "sem alterar configuracoes. Privilegios controlam operacoes no SO (shutdown, backup, "
        "take ownership, drivers); diferem das permissoes NTFS (acesso a recursos).",
        st["Body"]))

    story.append(Paragraph("2. Ferramentas Utilizadas", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade"],
        [
            ["whoami /priv", "Privilegios presentes no Access Token"],
            ["secpol.msc / secedit", "User Rights Assignment (politica local)"],
            ["gpedit.msc", "Politicas locais de seguranca / comportamento"],
            ["whoami /all", "Correlacionar identidade, grupos e privilegios"],
            ["PowerShell", "Automacao e consulta administrativa"],
            ["MMC", "Centralizar snap-ins administrativos"],
            ["Event Viewer / Get-WinEvent", "Eventos relacionados a privilegios/seguranca"],
            ["Consolidacao", "Sintese da auditoria e recomendacoes"],
        ],
        st, [5.0*cm, 11.7*cm]
    ))

    story.append(Paragraph("3. Evidencias Produzidas", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_whoami_priv", st))
    story.append(shot(paths, "03_user_rights_secedit", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_gpedit_status", st))
    story.append(shot(paths, "05_whoami_all", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_powershell_security", st))
    story.append(shot(paths, "07_mmc_equiv", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_event_viewer", st))
    story.append(shot(paths, "09_consolidacao", st))

    story.append(Paragraph("4. Resultados Obtidos", st["H1"]))
    story.append(Paragraph("4.1 Access Token — whoami /priv (Ex.1)", st["H2"]))
    story.append(Paragraph(
        "<b>5</b> privilegios listados na sessao atual. <b>Ativada:</b> apenas "
        "<b>SeChangeNotifyPrivilege</b> (bypass traverse). <b>Desativados:</b> SeShutdownPrivilege, "
        "SeUndockPrivilege, SeIncreaseWorkingSetPrivilege, SeTimeZonePrivilege.<br/>"
        "Relevancia: sessao em integridade media (UAC) — token filtrado. Mesmo sendo membro de "
        "Administradores, privilegios sensiveis nao estao todos Enabled ate elevacao. "
        "Ainda assim, a <b>capacidade de elevar</b> permanece (ConsentPrompt).",
        st["Body"]))

    story.append(Paragraph("4.2 User Rights / Politicas locais (Ex.2–3)", st["H2"]))
    story.append(Paragraph(
        "<b>secpol.msc / gpedit.msc:</b> <b>ausentes</b> no Windows 11 Home desta estacao. "
        "<b>secedit /export USER_RIGHTS:</b> negado sem elevacao administrativa — evidencia do "
        "proprio controle de privilegio.<br/>"
        "<b>UAC:</b> EnableLUA=1; ConsentPromptBehaviorAdmin=5; PromptOnSecureDesktop=1 — "
        "elevacao sob demanda com desktop seguro. Politicas locais reforcam comportamento de "
        "consentimento e reduzem uso acidental de privilegios elevados.",
        st["Body"]))

    story.append(Paragraph("4.3 Correlacao identidade/grupos/privilegios (Ex.4–6)", st["H2"]))
    story.append(Paragraph(
        "<b>whoami /all:</b> confirma SID, grupos e privilegios no mesmo token. "
        "BUILTIN\\Administradores com atributo de negacao na sessao filtrada.<br/>"
        "<b>PowerShell:</b> Get-Command *Security* retornou 5 itens (NetSecurity + SecurityHealth*). "
        "Get-LocalGroupMember Administradores: <b>Administrador</b> + <b>marge</b>. "
        "Automacao padroniza auditorias repetidas.<br/>"
        "<b>MMC:</b> mmc.exe disponivel; snap-ins tipicos: Local Security Policy, Event Viewer, "
        "Computer Management — centralizam a administracao sem alterar a politica nesta auditoria.",
        st["Body"]))

    story.append(Paragraph("4.4 Event Viewer (Ex.7)", st["H2"]))
    story.append(Paragraph(
        "Logs Application e System habilitados (milhares de registros). Log <b>Security</b> "
        "inacessivel na sessao nao elevada (operacao nao autorizada) — lacuna operacional: "
        "eventos 4672 (privilegios especiais) exigem leitura administrativa. System amostrado "
        "(ex.: DCOM 10016). Categorias padrao: Application, Security, Setup, System, Forwarded.",
        st["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("5. Analise Tecnica", st["H1"]))
    story.append(Paragraph(
        "Grupos administrativos <b>nao sao</b> sinônimo de privilegios Enabled no token: o UAC "
        "filtra a sessao diaria. Porem o menor privilegio <b>nao esta plenamente aplicado</b> "
        "porque a conta de uso diario permanece no grupo Administradores (Lab 06A), permitindo "
        "elevacao permanente sob demanda.<br/>"
        "<b>Inconsistencias:</b> (1) admin permanente na conta diaria; (2) export User Rights "
        "bloqueado sem elevacao / ferramentas ausentes no Home; (3) Security log ilegivel sem "
        "admin — dificulta investigacao de abuso de privilegio; (4) conta postgres habilitada "
        "sem revisao formal de logon rights.<br/>"
        "<b>Discussao:</b> administrar privilegios corretamente reduz superficie de ataque e "
        "elevacao indevida; identidade + grupo + privilegio formam a cadeia de autorizacao.",
        st["Body"]))

    story.append(Paragraph("6. Recomendacoes", st["H1"]))
    story.append(grid(
        ["#", "Recomendacao", "Prioridade"],
        [
            ["1", "Conta diaria sem Administradores; admin nominativa + UAC/JIT", "Alta"],
            ["2", "Em Enterprise/Server: auditar User Rights via secpol elevado", "Alta"],
            ["3", "Preferir atribuicao de direitos a grupos, nao a usuarios", "Alta"],
            ["4", "Garantir leitura do Security log para auditar 4672/mudancas", "Media"],
            ["5", "Revisar logon rights da conta postgres (servico)", "Media"],
            ["6", "Automatizar whoami/priv + inventario de grupos via PowerShell", "Media"],
            ["7", "Avancar para Lab 06C (permissoes NTFS / ACL)", "Alta"],
        ],
        st, [1.2*cm, 12.5*cm, 3.0*cm], WARN
    ))

    story.append(Paragraph("7. Conclusao / Parecer", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Estacao", "WIN-ADM-01 / MachadoPC"),
        ("Escopo", "Auditoria de privilegios (sem alteracao)"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "A administracao observada esta <b>parcialmente compativel</b> com o menor privilegio: "
        "UAC reduz privilegios efetivos na sessao media, mas a associacao permanente ao grupo "
        "Administradores mantem superficie de elevacao. A auditoria produziu evidencias de token, "
        "grupos, UAC, limites da edicao Home e Event Viewer.<br/>"
        "<b>Parecer:</b> [X] <b>AUDITORIA CONCLUIDA — APTO PARA AVANCAR AO LAB 06C (NTFS)</b> "
        "com plano de reorganizacao de privilegios.<br/>"
        f"<b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("Checklist Final", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["whoami /priv analisado", "SIM"],
            ["User Rights / secpol (ou equivalente documentado)", "SIM"],
            ["gpedit/UAC / politicas locais", "SIM"],
            ["whoami /all correlacionado", "SIM"],
            ["PowerShell + MMC documentados", "SIM"],
            ["Event Viewer / Get-WinEvent", "SIM"],
            ["Consolidacao + recomendacoes + parecer", "SIM"],
            ["Nenhuma configuracao alterada", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))
    story.append(Paragraph(
        "Screenshots: lab06b/evidencias/shots/img/ | Scripts: lab06b/scripts/",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 06B - Privilegios + Screenshots"),
              onLaterPages=footer("Lab 06B - Privilegios + Screenshots"))
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
