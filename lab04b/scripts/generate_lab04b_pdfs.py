#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 04B PDFs: Ordem de Servico + Manutencao Continua do Hardening."""

from __future__ import annotations

import os
import re
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

BASE = Path(r"d:\MMB\workspace\hardening\lab04b")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab04B_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab04B_Manutencao_Continua_Hardening_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab04B_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab04B_Manutencao_Continua_Hardening_PREENCHIDO.pdf")

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
    ("01_ambiente", "Evidencia 1 - Ambiente WEB-01"),
    ("02_apt_update", "Evidencia 2 - apt update"),
    ("03_apt_upgradable", "Evidencia 3 - apt list --upgradable"),
    ("04_apt_upgrade", "Evidencia 4 - apt upgrade (security libexpat1)"),
    ("05_security_status", "Evidencia 5 - Status de seguranca (equiv. Debian)"),
    ("06_debsecan", "Evidencia 6 - debsecan (CVEs)"),
    ("08_lynis", "Evidencia 7 - Lynis audit (HI=69)"),
    ("09_aide", "Evidencia 8 - AIDE --check"),
    ("10_debsums", "Evidencia 9 - debsums -c"),
]


def font(size=14, bold=False):
    cands = [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf"]
    if bold:
        cands = [r"C:\Windows\Fonts\consolab.ttf"] + cands
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def render_terminal(text, title, out_path, max_lines=34):
    text = strip_ansi(text)
    lines = text.replace("\t", "    ").splitlines()
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + ["... (saida truncada) ..."]
    f, ft = font(13), font(12, True)
    line_h, pad_x, pad_y, title_h = 18, 16, 14, 34
    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    max_w = max((d.textbbox((0, 0), ln, font=f)[2] for ln in lines), default=700)
    max_w = max(max_w, d.textbbox((0, 0), title, font=ft)[2])
    w = min(max(max_w + pad_x * 2, 720), 1100)
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
        if ln.startswith("root@"):
            color = "#3fb950"
        elif "upgradable" in ln.lower() or "CVE-" in ln or "Changed" in ln or "differences" in ln:
            color = "#ff7b72"
        elif "Hardening index" in ln or "Hit:" in ln or "upgraded" in ln or "OK" in ln or "0 warnings" in ln:
            color = "#79c0ff"
        elif ln.startswith("#") or ln.startswith("Conclusao"):
            color = "#8b949e"
        draw.text((pad_x, y), ln[:160], font=f, fill=color)
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
    s.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=14,
                         textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6, leading=17))
    s.add(ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=10,
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
        canvas.drawRightString(A4[0]-1.4*cm, A4[1]-1.0*cm, "AmazonTech WEB-01")
        canvas.line(1.4*cm, 1.2*cm, A4[0]-1.4*cm, 1.2*cm)
        canvas.drawCentredString(A4[0]/2, 0.75*cm,
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | Lynis HI=69")
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
    tw = width
    th = tw * (h / w)
    if th > 8.5*cm:
        th = 8.5*cm
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
                            title="Lab 04B - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 04B", st["CoverTitle"]))
    story.append(Paragraph("Manutencao Continua do Hardening Linux", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph("Status: CONCLUIDA | Lynis HI=69 | security update aplicada", st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Servidor", "WEB-01 (MachadoPC) - Debian 13.6"),
        ("Tipo", "Monitoramento, auditoria e manutencao continua"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Necessidades x Tratamento", st["H1"]))
    story.append(grid(
        ["Situacao", "Acao / Resultado", "Status"],
        [
            ["Atualizacoes pendentes", "1 pacote (libexpat1 security) - aplicado", "Resolvido"],
            ["Atualizacoes de seguranca", "Debian-Security: libexpat1 2.8.2-1~deb13u1", "Aplicado"],
            ["Boletins / bases de seguranca", "security.debian.org + debsecan (381 CVEs unicos)", "Consultado"],
            ["Vulnerabilidades conhecidas", "debsecan; priorizar openssh/libc6 em ciclo", "Avaliado"],
            ["Integridade de arquivos", "AIDE check + debsums -c (0 mismatches)", "Validado"],
            ["Auditoria de configuracao", "Lynis HI=69; 0 warnings; 48 suggestions", "Auditado"],
            ["Evidencias", "lab04b/evidencias + PDFs", "Produzido"],
        ],
        st, [4.8*cm, 8.7*cm, 2.7*cm], OK
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "02_apt_update", st))
    story.append(shot(paths, "04_apt_upgrade", st))
    story.append(PageBreak())
    story.append(shot(paths, "08_lynis", st))
    story.append(shot(paths, "09_aide", st))
    story.append(shot(paths, "10_debsums", st))

    story.append(Paragraph("4. Conformidade Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Servidor permanentemente atualizado", "SIM"],
            ["2. Prioridade a atualizacoes de seguranca", "SIM"],
            ["3. Boletins/avisos consultados regularmente", "SIM"],
            ["4. Auditoria periodica da configuracao", "SIM"],
            ["5. Alteracoes de integridade investigadas", "SIM"],
            ["6. Evidencias tecnicas produzidas", "SIM"],
            ["7. Politica de Hardening revisada continuamente", "SIM"],
            ["8. Ferramentas complementam protecoes existentes", "SIM"],
            ["9. Minima indisponibilidade observada", "SIM"],
            ["10. Conclusoes subsidiam politica integrada (Aula 5)", "SIM"],
        ],
        st, [13.5*cm, 3.2*cm], OK
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - ciclo de manutencao continua executado e documentado"),
        ("Documento tecnico", "Lab04B_Manutencao_Continua_Hardening_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 04B - Ordem de Servico"),
              onLaterPages=footer("Lab 04B - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 04B - Manutencao Continua", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 04B", st["CoverTitle"]))
    story.append(Paragraph("Manutencao Continua da Politica de Hardening - WEB-01", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Data: {DATE} | Lynis HI=69",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Objetivo da Atividade", st["H1"]))
    story.append(Paragraph(
        "Avaliar o estado atual do WEB-01 em operacao assistida e estabelecer rotinas de "
        "manutencao continua: atualizacao do SO, gerenciamento de vulnerabilidades, auditoria "
        "de configuracao e monitoramento de integridade. Hardening nao termina na implantacao; "
        "sem ciclo continuo, patches atrasados e desvios de config reabrem a superficie de ataque.",
        st["Body"]))

    story.append(Paragraph("2. Caracterizacao do Ambiente", st["H1"]))
    story.append(kv([
        ("Distribuicao Linux", "Debian GNU/Linux 13 (trixie)"),
        ("Versao", "13.6"),
        ("Maquina / hostname", "WEB-01 / MachadoPC"),
        ("Ambiente", "Laboratorio de Hardening (ciclo Labs 01-04A concluidos)"),
        ("Data da atividade", DATE),
        ("Equipe", TEAM),
    ], st))

    # Etapa 1
    story.append(Paragraph("3. Atualizacao do Sistema Operacional", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Finalidade", "Resultado obtido"],
        [
            ["apt update", "Sincronizar indices", "Hit em trixie, trixie-updates, trixie-security, backports"],
            ["apt list --upgradable", "Listar pendencias", "1 pacote: libexpat1 (stable-security)"],
            ["apt upgrade", "Aplicar atualizacoes", "libexpat1 2.7.1-2 -> 2.8.2-1~deb13u1 (security)"],
        ],
        st, [3.5*cm, 4.5*cm, 8.7*cm]
    ))
    story.append(Paragraph(
        "<b>Quantidade de atualizacoes:</b> 1. "
        "<b>Relacionadas a seguranca?</b> [X] Sim — origem Debian-Security. "
        "Repositorios acessados sem erro. Prioridade: security antes de updates funcionais. "
        "Em producao: janela, rollback e testes; neste lab a atualizacao foi aplicada (baixo impacto).",
        st["Body"]))
    story.append(shot(paths, "02_apt_update", st))
    story.append(PageBreak())
    story.append(shot(paths, "03_apt_upgradable", st))
    story.append(shot(paths, "04_apt_upgrade", st))

    # Etapa 2
    story.append(Paragraph("4. Gerenciamento de Vulnerabilidades", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Resultado observado"],
        [
            ["ubuntu-security-status", "N/A no Debian; equivalente: 547 pacotes ii + repo trixie-security ativo"],
            ["debsecan", "381 CVEs unicos / 815 linhas; inclui openssh-server/client e libc6"],
            ["dnf updateinfo", "N/A (Rocky); no Debian usamos security pocket + debsecan"],
        ],
        st, [4.5*cm, 12.2*cm]
    ))
    story.append(grid(
        ["Vulnerabilidade / pacote", "Criticidade", "Acao recomendada"],
        [
            ["libexpat1 (security update)", "Alta (security)", "Aplicada neste ciclo"],
            ["openssh-server/client (CVEs debsecan)", "Alta (servico exposto)", "Acompanhar DSA; patch em janela"],
            ["libc6 (CVEs debsecan)", "Alta (base)", "Priorizar; pode exigir reboot"],
            ["Demais CVEs debsecan", "Variavel", "Triagem semanal; nem todos exigem acao imediata"],
        ],
        st, [6.5*cm, 3.5*cm, 6.7*cm], WARN
    ))
    story.append(Paragraph(
        "<b>Discussao:</b> Nem todo CVE debsecan exige patch imediato (falso positivo / mitigacao / "
        "ainda sem fix no suite). Criticidade do servico (SSH) eleva prioridade. Atualizar sem "
        "planejamento pode causar indisponibilidade — equilibrar via janelas e testes.",
        st["Body"]))
    story.append(shot(paths, "05_security_status", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_debsecan", st))

    # Etapa 3
    story.append(Paragraph("5. Auditoria da Configuracao", st["H1"]))
    story.append(grid(
        ["Item", "Resultado"],
        [
            ["Lynis", "3.1.4 audit system"],
            ["Hardening Index", "69"],
            ["Warnings", "0"],
            ["Suggestions", "48"],
        ],
        st, [5.0*cm, 11.7*cm]
    ))
    story.append(Paragraph(
        "<b>5 principais recomendacoes:</b><br/>"
        "1) Politica de senha (AUTH-9286 / pam_pwquality).<br/>"
        "2) needrestart apos upgrades (DEB-0831).<br/>"
        "3) auditd (ACCT-9628).<br/>"
        "4) Malware scanner periodico (HRDN-7230).<br/>"
        "5) Fortalecer hashes AIDE SHA256/512 (FINT-4402).",
        st["Body"]))
    story.append(shot(paths, "08_lynis", st))

    story.append(Paragraph("6. Verificacao da Integridade", st["H1"]))
    story.append(grid(
        ["Ferramenta", "Resultado"],
        [
            ["AIDE --check", "Diferencas vs baseline (esperado: labels SELinux Lab04A + upgrade)"],
            ["debsums -c", "0 inconsistencias (exit 0)"],
        ],
        st, [4.0*cm, 12.7*cm]
    ))
    story.append(Paragraph(
        "<b>Alteracoes relevantes?</b> [X] Sim no AIDE — majoritariamente xattrs SELinux e arquivos "
        "tocados por manutencao; <b>nao</b> tratadas automaticamente como incidente. "
        "debsums sem mismatches nos checksums de pacotes. "
        "Antes de medida corretiva: classificar mudanca (legitima vs suspeita), correlacionar com "
        "change log, so entao atualizar baseline AIDE.",
        st["Body"]))
    story.append(PageBreak())
    story.append(shot(paths, "09_aide", st))
    story.append(shot(paths, "10_debsums", st))

    story.append(Paragraph("7. Consolidacao das Evidencias", st["H1"]))
    story.append(grid(
        ["Evidencia", "Ferramenta", "Finalidade"],
        [
            ["02/03/04 apt", "apt", "Atualizacao e security patch"],
            ["05 security status", "apt/sources", "Cobertura de repositorios security"],
            ["06 debsecan", "debsecan", "CVEs conhecidos"],
            ["08 lynis", "Lynis", "Auditoria Hardening Index"],
            ["09 aide", "AIDE", "Integridade vs baseline"],
            ["10 debsums", "debsums", "Checksums de pacotes"],
        ],
        st, [4.0*cm, 3.5*cm, 9.2*cm]
    ))

    # Plano
    story.append(Paragraph("8. Plano Permanente de Manutencao do Hardening", st["H1"]))
    story.append(Paragraph(
        "<b>Atualizacoes:</b> apt update diario; list --upgradable; security em ate 7 dias "
        "(criticos 24-72h); testes em homolog; janela com rollback; registrar evidencias.<br/>"
        "<b>Vulnerabilidades:</b> debsecan semanal; acompanhar DSA/security.debian.org; priorizar "
        "por exposicao (SSH, libs base); registrar CVE e acao.<br/>"
        "<b>Auditorias:</b> Lynis mensal (ou apos mudanca relevante); revisar suggestions; "
        "acompanhar evolucao do HI.<br/>"
        "<b>Integridade:</b> AIDE check semanal + apos upgrades; debsums mensal; investigar diffs; "
        "atualizar DB so apos validacao.<br/>"
        "<b>Documentacao:</b> data, responsavel, ferramentas, evidencias, recomendacoes, pendencias.",
        st["Body"]))

    story.append(Paragraph("9. Discussao Tecnica", st["H1"]))
    story.append(Paragraph(
        "<b>1.</b> Atualizar aplica patches; manter seguranca continuamente inclui auditoria, "
        "integridade, vulnerabilidades e revisao de politica.<br/>"
        "<b>2.</b> apt reduz CVEs conhecidos; debsecan prioriza; Lynis acha desvios de config; "
        "AIDE/debsums detectam alteracoes — juntos fecham o ciclo.<br/>"
        "<b>3. Frequencias:</b>",
        st["Body"]))
    story.append(grid(
        ["Frequencia", "Atividades"],
        [
            ["Diariamente", "apt update; revisar falhas de auth/Fail2Ban; checar alertas"],
            ["Semanalmente", "apt upgrade security; debsecan; AIDE --check; revisar diffs"],
            ["Mensalmente", "Lynis audit; debsums; revisar plano; atualizar baseline AIDE se OK"],
        ],
        st, [3.5*cm, 13.2*cm]
    ))
    story.append(Paragraph(
        "<b>4. Evidencias indispensaveis:</b> logs apt, saida debsecan, report Lynis (HI), "
        "relatorio AIDE, debsums, registro de mudancas.<br/>"
        "<b>5. Futuras alteracoes:</b> change control, re-auditoria Lynis, AIDE check pos-mudanca, "
        "menor privilegio e MAC (Lab04A) preservados.",
        st["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("10. Parecer Tecnico", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Servidor", "WEB-01"),
        ("Atualizacoes", "Em dia apos patch security libexpat1"),
        ("Vulnerabilidades", "Monitoradas via debsecan; triagem continua"),
        ("Auditoria", "Lynis HI=69; 0 warnings"),
        ("Integridade", "AIDE operacional; debsums OK"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "<b>Riscos:</b> CVEs remanescentes no debsecan (triagem); HI 69 indica melhorias "
        "(senha, auditd, malware scanner); diffs AIDE exigem disciplina de baseline.<br/>"
        "<b>Recomendacoes prioritarias:</b> (1) ciclo semanal security+debsecan; (2) pam/senha; "
        "(3) auditd; (4) atualizar baseline AIDE apos validar Lab04A; (5) needrestart.<br/>"
        "<b>Conclusao:</b> [X] <b>APTO PARA OPERACAO ASSISTIDA</b> com plano permanente de "
        "manutencao instituido. Hardening passa a ser processo continuo ate o Projeto Integrador "
        "(Aula 5).<br/>"
        f"<b>Responsavel:</b> {TEAM}<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("11. Conclusoes", st["H1"]))
    story.append(Paragraph(
        "Atualizacao, vulnerabilidades, auditoria e integridade sao pilares complementares. "
        "Ferramentas usadas (apt, debsecan, Lynis, AIDE, debsums) formam um ciclo operacional "
        "reutilizavel. Dificuldade tipica: interpretar volume de CVEs e diffs AIDE sem alarmismo. "
        "O Lab 04B prepara a equipe para o Projeto Integrador com checklist e plano permanentes.",
        st["Body"]))

    story.append(Paragraph("Apendice B — Checklist Operacional de Hardening", st["H1"]))
    story.append(grid(
        ["Atividade", "Status", "Evidencia"],
        [
            ["Sistema atualizado", "SIM", "04_apt_upgrade (libexpat1)"],
            ["Atualizacoes de seguranca verificadas", "SIM", "03/04 + security.debian.org"],
            ["Vulnerabilidades analisadas", "SIM", "06_debsecan"],
            ["Auditoria executada", "SIM", "08_lynis HI=69"],
            ["Integridade verificada", "SIM", "09_aide + 10_debsums"],
            ["Evidencias registradas", "SIM", "lab04b/evidencias"],
            ["Plano de manutencao atualizado", "SIM", "Secao 8 deste relatorio"],
        ],
        st, [7.5*cm, 2.2*cm, 7.0*cm], OK
    ))

    story.append(Paragraph(
        "Screenshots: lab04b/evidencias/shots/img/ | Scripts: lab04b/scripts/",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 04B - Manutencao Continua + Screenshots"),
              onLaterPages=footer("Lab 04B - Manutencao Continua + Screenshots"))
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
