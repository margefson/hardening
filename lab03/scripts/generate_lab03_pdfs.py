#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 03 PDFs: Ordem de Servico + Reducao da Superficie de Ataque."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab03")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab03_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab03_Reducao_Superficie_Ataque_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab03_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab03_Reducao_Superficie_Ataque_PREENCHIDO.pdf")

TEAM = "Josias Bentes, Keven Coimbra, Margefson Barros e Nattan Lobato"
TEAM_SHORT = "Josias, Keven, Margefson, Nattan"

PRIMARY = HexColor("#1a365d")
ACCENT = HexColor("#2c5282")
LIGHT = HexColor("#edf2f7")
OK = HexColor("#276749")
WARN = HexColor("#c05621")
BORDER = HexColor("#cbd5e0")

SHOT_META = [
    ("01_inventario_servicos", "Evidencia 1 - Inventario de servicos"),
    ("02_portas", "Evidencia 2 - Portas e processos em escuta"),
    ("03_menor_func", "Evidencia 3 - Menor funcionalidade (servicos desabilitados)"),
    ("04_ssh_status", "Evidencia 4 - Hardening SSH"),
    ("05_ufw", "Evidencia 5 - Politica UFW (default deny + SSH)"),
    ("06_fail2ban", "Evidencia 6 - Fail2Ban jail sshd"),
    ("07_aide", "Evidencia 7 - AIDE baseline FULL (sem /mnt WSL) + deteccao"),
    ("08_lynis", "Evidencia 8 - Lynis Hardening Index = 69"),
]


def font(size=14, bold=False):
    cands = [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf"]
    if bold:
        cands = [r"C:\Windows\Fonts\consolab.ttf"] + cands
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_terminal(text, title, out_path, max_lines=30):
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
        elif "differences" in ln or "Changed" in ln or "warning" in ln.lower():
            color = "#ff7b72"
        elif "NO differences" in ln or "Looks okay" in ln or "hardening_index" in ln or "active" in ln:
            color = "#79c0ff"
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
                                 f"Pag. {doc.page} | 30/07/2026 | Equipe: {TEAM_SHORT} | Lynis HI=69")
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
    if th > 9.0*cm:
        th = 9.0*cm
        tw = th * (w / h)
    return KeepTogether([
        RLImage(str(p), width=tw, height=th),
        Paragraph(f"<i>Figura - {dict(SHOT_META)[key]}</i>", st["Cap"]),
    ])


def hr():
    return HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=5)


def build_os(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_OS), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 03 - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 03", st["CoverTitle"]))
    story.append(Paragraph("Reducao da Superficie de Ataque", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph("Status: CONCLUIDA | Lynis Hardening Index = 69", st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Servidor", "WEB-01 (MachadoPC) - Debian 13.6"),
        ("Tipo", "Auditoria, reducao de superficie, hardening e validacao"),
        ("Data", "30/07/2026"),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Problemas x Tratamento", st["H1"]))
    story.append(grid(
        ["Problema", "Acao", "Status"],
        [
            ["Servicos legados / sem justificativa", "Disable e2scrub_reap e exim4", "Resolvido"],
            ["SSH com config padrao / ausente", "Instalado + hardening (root no, X11 no)", "Resolvido"],
            ["Firewall inexistente/permissivo", "UFW default deny + allow OpenSSH", "Resolvido"],
            ["Sem resposta automatica a brute-force", "Fail2Ban jail sshd ativa", "Resolvido"],
            ["Sem monitoramento de integridade", "AIDE baseline + deteccao validada", "Resolvido"],
            ["Sem auditoria de hardening", "Lynis audit system (HI=69)", "Resolvido"],
        ],
        st, [6.2*cm, 7.5*cm, 2.5*cm], WARN
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "01_inventario_servicos", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_ssh_status", st))
    story.append(shot(paths, "05_ufw", st))
    story.append(shot(paths, "06_fail2ban", st))
    story.append(PageBreak())
    story.append(shot(paths, "07_aide", st))
    story.append(shot(paths, "08_lynis", st))

    story.append(Paragraph("4. Conformidade com a Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Todo servico ativo com justificativa", "SIM"],
            ["2. Servicos desnecessarios desabilitados", "SIM"],
            ["3. Configuracao padrao revisada", "SIM"],
            ["4. Acesso remoto endurecido (SSH)", "SIM"],
            ["5. Apenas comunicacoes necessarias (UFW)", "SIM"],
            ["6. Eventos suspeitos tratados (Fail2Ban)", "SIM"],
            ["7. Integridade monitorada (AIDE)", "SIM"],
            ["8. Auditorias periodicas (Lynis)", "SIM"],
            ["9. Validacao apos alteracoes", "SIM"],
            ["10. Evidencias registradas", "SIM"],
        ],
        st, [13.5*cm, 3.2*cm], OK
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - controles Lab 03 implementados e validados"),
        ("Documento tecnico", "Lab03_Reducao_Superficie_Ataque_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 03 - Ordem de Servico"),
              onLaterPages=footer("Lab 03 - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 03 - Reducao da Superficie de Ataque", author=TEAM)
    story = []
    story.append(Paragraph("LABORATORIO 03 - RELATORIO TECNICO", st["CoverSub"]))
    story.append(Paragraph("Reducao da Superficie de Ataque", st["CoverTitle"]))
    story.append(Paragraph("Windows e Linux Hardening - Aula 3", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph("AmazonTech | WEB-01 | Debian 13.6 | 30/07/2026 | Lynis HI=69", st["Meta"]))
    story.append(hr())

    # M1
    story.append(Paragraph("Missao 1 - Inventario da Superficie de Ataque", st["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Servicos essenciais: cron, dbus, rsyslog, journald, ssh (apos instalacao). "
        "Portas: 22/tcp (sshd), DNS WSL interno. Classificacao: ssh=administrativo essencial; "
        "e2scrub_reap/exim4=candidatos a remocao; getty=console.",
        st["Body"]))
    story.append(shot(paths, "01_inventario_servicos", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_portas", st))
    story.append(Paragraph(
        "<b>Reflexao M1:</b> Nem todo servico ativo e vulnerabilidade; porta aberta so e risco se "
        "exposta e mal configurada. Inventario deve anteceder hardening para evitar remocoes cegas.",
        st["Body"]))

    # M2
    story.append(Paragraph("Missao 2 - Menor Funcionalidade", st["H1"]))
    story.append(hr())
    story.append(grid(
        ["Servico", "Inicial", "Decisao", "Final", "Justificativa"],
        [
            ["ssh", "Ausente/padrao", "Manter+endurecer", "Ativo", "Admin remota"],
            ["e2scrub_reap", "enabled", "Desabilitar", "disabled", "Nao essencial no lab WSL"],
            ["exim4", "ativo (dep)", "Desabilitar", "disabled", "SMTP nao necessario"],
            ["cron/rsyslog", "ativo", "Manter", "ativo", "Operacao/auditoria"],
        ],
        st, [3.0*cm, 3.0*cm, 3.2*cm, 2.5*cm, 5.0*cm]
    ))
    story.append(shot(paths, "03_menor_func", st))

    # M3
    story.append(PageBreak())
    story.append(Paragraph("Missao 3 - Hardening SSH", st["H1"]))
    story.append(hr())
    story.append(grid(
        ["Parametro", "Inicial", "Avaliacao", "Final", "Justificativa"],
        [
            ["PermitRootLogin", "padrao/yes", "Revisar", "no", "Evitar login root direto"],
            ["PasswordAuthentication", "yes", "Manter (lab)", "yes", "Lab; prod preferir chaves"],
            ["PubkeyAuthentication", "yes", "Manter", "yes", "Autenticacao robusta"],
            ["X11Forwarding", "yes", "Revisar", "no", "Reduz superficie"],
            ["MaxAuthTries", "padrao", "Revisar", "3", "Limita brute-force"],
            ["AllowUsers", "livre", "Revisar", "machado carlos", "Menor privilegio"],
        ],
        st, [3.5*cm, 2.5*cm, 2.5*cm, 3.0*cm, 4.2*cm]
    ))
    story.append(shot(paths, "04_ssh_status", st))

    # M4
    story.append(Paragraph("Missao 4 - Firewall UFW", st["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Politica: default deny incoming / allow outgoing; allow OpenSSH (22/tcp). "
        "HTTP nao liberado (sem app web neste lab). Porta em escuta != porta acessivel.",
        st["Body"]))
    story.append(shot(paths, "05_ufw", st))

    # M5
    story.append(PageBreak())
    story.append(Paragraph("Missao 5 - Fail2Ban", st["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Jail sshd ativa (maxretry=3, bantime=10m). Nao substitui firewall nem hardening SSH; "
        "complementa defesa em profundidade via analise de logs.",
        st["Body"]))
    story.append(shot(paths, "06_fail2ban", st))

    # M6
    story.append(Paragraph("Missao 6 - AIDE", st["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Baseline FULL Debian via aideinit (~96s, DB 6.1M), com exclusoes WSL "
        "(/mnt, /usr/lib/wsl, modules) para nao varrer C:/D:/F:. "
        "Check detectou alteracoes incluindo /etc/hosts na simulacao controlada. "
        "AIDE nao impede alteracoes; detecta e exige analise.",
        st["Body"]))
    story.append(shot(paths, "07_aide", st))

    # M7
    story.append(PageBreak())
    story.append(Paragraph("Missao 7 - Auditoria Lynis", st["H1"]))
    story.append(hr())
    story.append(shot(paths, "08_lynis", st))
    story.append(grid(
        ["Recomendacao", "Prioridade", "Justificativa"],
        [
            ["SSH-7408 (AllowTcpForwarding/MaxSessions etc.)", "Alta", "Aprofundar hardening SSH"],
            ["AUTH-9286 PASS_MAX_DAYS / password age", "Alta", "Politica de senha"],
            ["ACCT-9628 auditd", "Media", "Trilha de auditoria"],
            ["PKGS-7420 unattended-upgrades", "Media", "Patches automaticos"],
            ["HRDN-7230 malware scanner", "Baixa-Media", "Complementar FIM"],
            ["BANN-7126 login banner", "Baixa", "Aviso legal"],
        ],
        st, [7.5*cm, 2.5*cm, 6.7*cm], WARN
    ))
    story.append(Paragraph(
        "<b>Plano de melhoria (3 itens):</b><br/>"
        "1) SSH adicional (AllowTcpForwarding no) - Equipe Infra - 7 dias - reduz abuso de tunel.<br/>"
        "2) PASS_MAX_DAYS/pam_pwquality - Equipe Seguranca - 14 dias - credenciais mais fortes.<br/>"
        "3) auditd + unattended-upgrades - Equipe Infra - 21 dias - deteccao e patch continuo.",
        st["Body"]))

    story.append(Paragraph("Checklist Final", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["Inventario da superficie de ataque", "SIM"],
            ["Servicos classificados / menor funcionalidade", "SIM"],
            ["SSH revisado e validado (sshd -t)", "SIM"],
            ["Politica de firewall UFW", "SIM"],
            ["Fail2Ban configurado", "SIM"],
            ["AIDE inicializado e testado", "SIM"],
            ["Auditoria Lynis executada (HI=69)", "SIM"],
            ["Evidencias coletadas + parecer", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))

    story.append(Paragraph("Parecer Tecnico de Auditoria de Hardening", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Servidor", "WEB-01"),
        ("Data", "30/07/2026"),
        ("Equipe Responsavel", TEAM),
        ("Hardening Index (Lynis)", "69"),
    ], st))
    story.append(Paragraph(
        "<b>1. Objetivo:</b> verificar reducao de superficie, SSH, firewall, Fail2Ban, AIDE e auditoria.<br/>"
        "<b>2. Situacao inicial:</b> servicos sem justificativa; SSH ausente/padrao; firewall inativo; "
        "sem Fail2Ban/AIDE/Lynis.<br/>"
        "<b>3. Controles:</b> inventario; disable e2scrub_reap/exim4; SSH endurecido; UFW deny+SSH; "
        "Fail2Ban sshd; AIDE baseline+deteccao; Lynis HI=69.<br/>"
        "<b>4. Analise:</b> superficie reduzida; servicos essenciais disponiveis; comunicacao controlada; "
        "protecao automatica e FIM operacionais; ainda ha melhorias Lynis (SSH fino, senha, auditd).<br/>"
        "<b>5. Conclusao / Parecer final:</b> [X] O servidor necessita apenas de <b>pequenos ajustes</b> "
        "antes da entrada em producao (Hardening Index 69; controles principais do Lab 03 concluidos). "
        "Hardening e processo continuo.<br/>"
        "<b>Responsavel tecnico:</b> " + TEAM + "<br/><b>Data:</b> 30/07/2026",
        st["Body"]))
    story.append(Paragraph("Screenshots: evidencias/shots/img/ | Evidencias: evidencias/lab03_evidence*.txt", st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 03 - Reducao da Superficie + Screenshots"),
              onLaterPages=footer("Lab 03 - Reducao da Superficie + Screenshots"))
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
