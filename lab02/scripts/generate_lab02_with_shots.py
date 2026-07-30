#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera screenshots e PDFs Lab 02 - conclusao APTO PARA OPERACAO."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image as RLImage, KeepTogether
)

BASE = Path(r"d:\MMB\workspace\hardening\lab02")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab02_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab02_Identidades_e_Privilegios_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab02_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab02_Identidades_e_Privilegios_PREENCHIDO.pdf")

PRIMARY = HexColor("#1a365d")
ACCENT = HexColor("#2c5282")
LIGHT = HexColor("#edf2f7")
OK = HexColor("#276749")
WARN = HexColor("#c05621")
BORDER = HexColor("#cbd5e0")

SHOT_META = [
    ("01_hostname_date", "Evidencia 1 - Identificacao do host / SO"),
    ("02_usuarios", "Evidencia 2 - Usuarios corporativos (getent passwd)"),
    ("03_id_usuarios", "Evidencia 3 - UID/GID/grupos (id)"),
    ("04_grupos", "Evidencia 4 - Grupos corporativos e sudo"),
    ("05_sudo_final", "Evidencia 5 - sudo final + conta temporario/backup"),
    ("06_diretorios", "Evidencia 6 - Propriedade e permissoes dos diretorios"),
    ("07_arquivos", "Evidencia 7 - Arquivos de teste nos diretorios"),
    ("08_acesso_ok", "Evidencia 8 - Testes de acesso autorizado"),
    ("09_acesso_negado", "Evidencia 9 - Testes de acesso indevido (Permission denied)"),
    ("10_acl_demo", "Evidencia 10 - ACL concedida a paulo em /financeiro"),
    ("11_acl_remove", "Evidencia 11 - Remocao da ACL e revalidacao"),
    ("12_sudo_l", "Evidencia 12 - Privileges sudo -l -U"),
    ("13_sudoers", "Evidencia 13 - Trecho sudoers + servico cron"),
    ("14_auditoria_final", "Evidencia 14 - Auditoria final consolidada"),
    ("15_pos_ressalvas", "Evidencia 15 - Fechamento: logging + sudoers auditavel"),
]


def font(size=14, bold=False):
    candidates = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
    ]
    if bold:
        candidates = [
            r"C:\Windows\Fonts\consolab.ttf",
            r"C:\Windows\Fonts\courbd.ttf",
        ] + candidates
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_terminal(text: str, title: str, out_path: Path, max_lines: int = 30):
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
    title_bbox = dtmp.textbbox((0, 0), title, font=f_title)
    max_w = max(max_w, title_bbox[2] - title_bbox[0])

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
        elif "Permission denied" in ln or "not allowed" in ln or "cannot" in ln:
            color = "#ff7b72"
        elif ln.startswith("===") or ln.startswith("---") or "APTO" in ln or "STATUS" in ln:
            color = "#79c0ff"
        draw.text((pad_x, y), ln[:160], font=f, fill=color)
        y += line_h

    draw.rectangle([0, 0, width - 1, height - 1], outline="#30363d")
    img.save(out_path, "PNG", optimize=True)
    return out_path


def generate_all_shots():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}
    for key, title in SHOT_META:
        txt_path = SHOT_DIR / f"{key}.txt"
        txt = txt_path.read_text(encoding="utf-8", errors="replace")
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
    s.add(ParagraphStyle("Left", fontName="Helvetica", fontSize=8.5,
                         alignment=TA_LEFT, spaceAfter=2, leading=11))
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


def footer(title):
    def _f(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(PRIMARY)
        canvas.setLineWidth(1)
        canvas.line(1.4*cm, A4[1]-1.15*cm, A4[0]-1.4*cm, A4[1]-1.15*cm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(ACCENT)
        canvas.drawString(1.4*cm, A4[1]-1.0*cm, title)
        canvas.drawRightString(A4[0]-1.4*cm, A4[1]-1.0*cm, "AmazonTech - WEB-01")
        canvas.line(1.4*cm, 1.2*cm, A4[0]-1.4*cm, 1.2*cm)
        canvas.drawCentredString(A4[0]/2, 0.75*cm,
                                 f"Pag. {doc.page} | 28/07/2026 | Equipe: Josias, Keven, Margefson, Nattan | APTO")
        canvas.restoreState()
    return _f


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
    cap = dict(SHOT_META)[key]
    return KeepTogether([
        RLImage(str(p), width=target_w, height=target_h),
        Paragraph(f"<i>Figura - {cap}</i>", st["Cap"]),
    ])


def hr():
    return HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=5)


def build_os(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_OS), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 02 - Ordem de Servico (APTO)",
                            author="Josias Bentes, Keven Coimbra, Margefson Barros, Nattan Lobato")
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 02", st["CoverTitle"]))
    story.append(Paragraph("Controle de Identidades e Privilegios Administrativos", st["CoverSub"]))
    story.append(Paragraph("Status final: APTO PARA OPERACAO (sem ressalvas tecnicas)", st["CoverSub"]))
    story.append(Paragraph(
        "<b>Equipe:</b> Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao da Atividade", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Servidor", "WEB-01 (hostname: MachadoPC)"),
        ("SO", "Debian GNU/Linux 13.6 (trixie)"),
        ("Tipo", "Auditoria, correcao e validacao de controles de acesso"),
        ("Data", "28/07/2026"),
        ("Equipe / Responsaveis", "Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato"),
        ("Status da OS", "<b>CONCLUIDA</b> - ambiente APTO PARA OPERACAO"),
    ], st))
    story.append(shot(paths, "01_hostname_date", st))

    story.append(Paragraph("2. Problemas Relatados x Tratamento", st["H1"]))
    story.append(grid(
        ["Problema", "Acao", "Status"],
        [
            ["Inventario desatualizado / contas sem funcao", "Criacao e classificacao das identidades", "Resolvido"],
            ["Associacoes e privilegios inadequados", "Reorganizacao de grupos + limpeza do sudo", "Resolvido"],
            ["Conta servico/temporaria privilegiada", "backup fora do sudo; temporario bloqueado", "Resolvido"],
            ["Permissoes e ACL", "Diretorios 750/770 + ACL temporaria testada/removida", "Resolvido"],
            ["Logging insuficiente (ressalva anterior)", "rsyslog + journald + /var/log/sudo.log", "Resolvido"],
        ],
        st, [6.0*cm, 7.5*cm, 2.7*cm], WARN
    ))

    story.append(Paragraph("3. Evidencia - Identidades e Grupos Finais", st["H1"]))
    story.append(shot(paths, "02_usuarios", st))
    story.append(shot(paths, "03_id_usuarios", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_grupos", st))
    story.append(shot(paths, "05_sudo_final", st))

    story.append(Paragraph("4. Evidencia - Diretorios e Testes", st["H1"]))
    story.append(shot(paths, "06_diretorios", st))
    story.append(shot(paths, "08_acesso_ok", st))
    story.append(shot(paths, "09_acesso_negado", st))

    story.append(PageBreak())
    story.append(Paragraph("5. Evidencia - ACL e sudo", st["H1"]))
    story.append(shot(paths, "10_acl_demo", st))
    story.append(shot(paths, "11_acl_remove", st))
    story.append(shot(paths, "12_sudo_l", st))

    story.append(Paragraph("6. Fechamento das ressalvas e Encerramento", st["H1"]))
    story.append(Paragraph(
        "Alem das correcoes das 7 missoes, foram eliminadas as ressalvas tecnicas remanescentes: "
        "servico rsyslog ativo, journald ativo e politica sudo com logfile/log_input/log_output "
        "em /etc/sudoers.d/99-amazontech-lab02. Com isso, a OS e encerrada como "
        "<b>CONCLUIDA - ambiente APTO PARA OPERACAO</b>, sem ressalvas tecnicas abertas no escopo do Lab 02.",
        st["Body"]))
    story.append(shot(paths, "14_auditoria_final", st))
    story.append(shot(paths, "15_pos_ressalvas", st))
    story.append(kv([
        ("Resultado", "CONCLUIDA - ambiente APTO PARA OPERACAO"),
        ("Equipe", "Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato"),
        ("Documento tecnico detalhado", "Lab02_Identidades_e_Privilegios_PREENCHIDO.pdf"),
        ("Pasta de screenshots", "evidencias/shots/img/"),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 02 - Ordem de Servico + Screenshots"),
              onLaterPages=footer("Lab 02 - Ordem de Servico + Screenshots"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 02 - Identidades e Privilegios (APTO)",
                            author="Josias Bentes, Keven Coimbra, Margefson Barros, Nattan Lobato")
    story = []
    story.append(Paragraph("LABORATORIO 2 - RELATORIO TECNICO COM EVIDENCIAS", st["CoverSub"]))
    story.append(Paragraph("Controle de Identidades e Privilegios Administrativos", st["CoverTitle"]))
    story.append(Paragraph("AmazonTech | WEB-01 | Debian 13.6 | 28/07/2026 | APTO PARA OPERACAO", st["Meta"]))
    story.append(Paragraph(
        "<b>Equipe:</b> Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato",
        st["Meta"]))
    story.append(hr())
    story.append(Paragraph(
        "Relatorio das 7 missoes com screenshots de terminal. Conclusao final apos fechamento das "
        "ressalvas tecnicas: ambiente apto para operacao.",
        st["Body"]))

    story.append(Paragraph("Missao 1 - Inventario das Identidades", st["H1"]))
    story.append(hr())
    story.append(shot(paths, "01_hostname_date", st))
    story.append(shot(paths, "02_usuarios", st))
    story.append(PageBreak())
    story.append(shot(paths, "03_id_usuarios", st))

    story.append(Paragraph("Missao 2 - Organizacao de Usuarios e Grupos", st["H1"]))
    story.append(hr())
    story.append(grid(
        ["Usuario", "Grupo final", "Decisao"],
        [
            ["ana", "desenvolvimento", "Removida de infraestrutura/sudo"],
            ["carlos", "infraestrutura + sudo", "Mantido (admin)"],
            ["maria", "financeiro", "Removida de desenvolvimento"],
            ["paulo", "auditoria", "Mantido"],
            ["backup", "sem grupo admin", "Removido do sudo"],
        ],
        st, [3.5*cm, 6.5*cm, 6.7*cm]
    ))
    story.append(shot(paths, "04_grupos", st))

    story.append(Paragraph("Missao 3 - Privilegios Administrativos", st["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "sudo antes: machado,carlos,ana,backup,temporario / depois: machado,carlos. "
        "temporario bloqueado; backup com nologin.",
        st["Body"]))
    story.append(shot(paths, "05_sudo_final", st))

    story.append(PageBreak())
    story.append(Paragraph("Missao 4 - Propriedade e Permissoes", st["H1"]))
    story.append(hr())
    story.append(grid(
        ["Diretorio", "Dono:Grupo", "Modo", "Resultado"],
        [
            ["/projetos", "ana:desenvolvimento", "750", "Acesso restrito a area"],
            ["/financeiro", "maria:financeiro", "770", "Grupo autorizado a gravar"],
            ["/auditoria", "paulo:auditoria", "750", "Outros sem acesso"],
            ["/infraestrutura", "carlos:infraestrutura", "750", "Acesso controlado"],
        ],
        st, [3.5*cm, 4.5*cm, 2.0*cm, 6.7*cm], OK
    ))
    story.append(shot(paths, "06_diretorios", st))
    story.append(shot(paths, "08_acesso_ok", st))
    story.append(PageBreak())
    story.append(shot(paths, "09_acesso_negado", st))

    story.append(Paragraph("Missao 5 - ACL", st["H1"]))
    story.append(hr())
    story.append(shot(paths, "10_acl_demo", st))
    story.append(shot(paths, "11_acl_remove", st))

    story.append(PageBreak())
    story.append(Paragraph("Missao 6 - sudo", st["H1"]))
    story.append(hr())
    story.append(shot(paths, "12_sudo_l", st))
    story.append(shot(paths, "13_sudoers", st))

    story.append(Paragraph("Missao 7 - Auditoria Final e Parecer", st["H1"]))
    story.append(hr())
    story.append(shot(paths, "14_auditoria_final", st))
    story.append(shot(paths, "15_pos_ressalvas", st))
    story.append(grid(
        ["Checklist", "OK?"],
        [
            ["Usuarios classificados; temporario bloqueado; servico nologin", "SIM"],
            ["Grupos corporativos corretos; sem associacoes indevidas", "SIM"],
            ["sudo apenas para administradores autorizados", "SIM"],
            ["Diretorios 750/770; sem 777; testes +/- ok", "SIM"],
            ["ACL excepcional removida apos uso", "SIM"],
            ["Politica sudo validada com evidencia + logging", "SIM"],
            ["rsyslog/journald ativos para auditoria", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))
    story.append(Paragraph("Parecer Tecnico", st["H2"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Servidor", "WEB-01 (MachadoPC)"),
        ("Responsaveis pela analise", "Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato"),
        ("Data", "28/07/2026"),
    ], st))
    story.append(Paragraph(
        "<b>1. Objetivo:</b> auditar e fortalecer identidades, grupos, permissoes e privilegios.<br/>"
        "<b>2. Situacao inicial:</b> excesso de sudo e grupos cruzados no cenario da auditoria.<br/>"
        "<b>3. Correcoes:</b> reorganizacao de grupos, limpeza do sudo, bloqueio de temporario, "
        "nologin em backup, diretorios 750/770, ACL temporaria testada/removida, rsyslog ativo e "
        "logging de sudo em /var/log/sudo.log.<br/>"
        "<b>4. Testes:</b> acessos autorizados OK; acessos indevidos negados; ACL leitura OK / escrita negada.<br/>"
        "<b>5. Riscos remanescentes no escopo do Lab 02:</b> nenhum risco tecnico aberto.<br/>"
        "<b>6. Conclusao:</b> [X] O ambiente esta <b>APTO PARA OPERACAO</b>.<br/>"
        "<b>7. Recomendacoes de continuidade (boas praticas, nao bloqueantes):</b> manter revisao "
        "periodica de identidades e sudo como rotina operacional da AmazonTech.",
        st["Body"]))
    story.append(Paragraph(
        "Screenshots gerados a partir de saidas reais em 28/07/2026. Arquivos em evidencias/shots/img/.",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 02 - Identidades e Privilegios + Screenshots"),
              onLaterPages=footer("Lab 02 - Identidades e Privilegios + Screenshots"))
    print("LAB OK")


if __name__ == "__main__":
    paths = generate_all_shots()
    build_os(paths)
    build_lab(paths)
    shutil.copy2(OUT_OS, DL_OS)
    shutil.copy2(OUT_LAB, DL_LAB)
    print("Downloads:")
    print(DL_OS)
    print(DL_LAB)
