#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 04A PDFs: Ordem de Servico + Mandatory Access Control (SELinux ativo)."""

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

BASE = Path(r"d:\MMB\workspace\hardening\lab04a")
SHOT_DIR = BASE / "evidencias" / "shots"
IMG_DIR = SHOT_DIR / "img"
OUT_OS = BASE / "entregaveis" / "Lab04A_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE / "entregaveis" / "Lab04A_Mandatory_Access_Control_PREENCHIDO.pdf"
DL_OS = Path(r"c:\Users\marge\Downloads\Lab04A_Ordem_de_Servico_PREENCHIDO.pdf")
DL_LAB = Path(r"c:\Users\marge\Downloads\Lab04A_Mandatory_Access_Control_PREENCHIDO.pdf")

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
    ("01_ambiente", "Evidencia 1 - Ambiente e LSM do kernel"),
    ("02_sestatus_getenforce", "Evidencia 2 - sestatus + getenforce (Enforcing)"),
    ("03_ls_Z", "Evidencia 3 - ls -Z (contextos SELinux)"),
    ("04_ps_Z", "Evidencia 4 - ps -Z (dominios de processos)"),
    ("05_restorecon", "Evidencia 5 - restorecon (restauracao de labels)"),
    ("06_semanage", "Evidencia 6 - semanage fcontext (5843 regras)"),
    ("07_apparmor_comparativo", "Evidencia 7 - AppArmor comparativo (user-space)"),
]


def font(size=14, bold=False):
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
        elif "Enforcing" in ln or "enabled" in ln or "Relabeled" in ln or "httpd_sys_content_t" in ln:
            color = "#79c0ff"
        elif "Disabled" in ln or "not mounted" in ln or "NAO" in ln:
            color = "#ff7b72"
        elif ln.startswith("#"):
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
                                 f"Pag. {doc.page} | {DATE} | Equipe: {TEAM_SHORT} | SELinux=Enforcing")
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
    OUT_OS.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT_OS), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 04A - Ordem de Servico", author=TEAM)
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Servico - Laboratorio 04A", st["CoverTitle"]))
    story.append(Paragraph("Mandatory Access Control (SELinux e AppArmor)", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph("Status: CONCLUIDA | SELinux Enforcing | Politica default", st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Identificacao", st["H1"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Unidade", "Gerencia de Infraestrutura e Seguranca da Informacao"),
        ("Servidor", "WEB-01 (MachadoPC) - Debian 13.6"),
        ("Tipo", "Auditoria, validacao e analise de mecanismos MAC"),
        ("Data", DATE),
        ("Equipe", TEAM),
        ("Status da OS", "<b>CONCLUIDA</b>"),
    ], st))

    story.append(Paragraph("2. Situacao inicial x Tratamento", st["H1"]))
    story.append(grid(
        ["Situacao", "Acao / Resultado", "Status"],
        [
            ["MAC presente no ambiente", "SELinux ativo no LSM do kernel; AppArmor analisado", "Resolvido"],
            ["Estado operacional", "sestatus=enabled; getenforce=Enforcing", "Validado"],
            ["Politica carregada", "Loaded policy name: default", "Confirmado"],
            ["Processos / contextos", "ps -Z com system_u:system_r:kernel_t:s0", "Identificado"],
            ["Labels de arquivos", "ls -Z: etc_t, shadow_t, sshd_exec_t, httpd_sys_content_t", "Analisado"],
            ["Ferramentas admin", "sestatus, getenforce, ls -Z, ps -Z, restorecon, semanage", "OK"],
            ["Evidencias", "Screenshots + saidas em lab04a/evidencias", "Produzido"],
        ],
        st, [4.8*cm, 8.7*cm, 2.7*cm], OK
    ))

    story.append(Paragraph("3. Evidencias principais", st["H1"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_sestatus_getenforce", st))
    story.append(shot(paths, "03_ls_Z", st))
    story.append(PageBreak())
    story.append(shot(paths, "05_restorecon", st))
    story.append(shot(paths, "06_semanage", st))

    story.append(Paragraph("4. Conformidade com a Politica AmazonTech", st["H1"]))
    story.append(grid(
        ["Diretriz", "Atendida?"],
        [
            ["1. Servidor com MAC quando suportado pela distro/kernel", "SIM"],
            ["2. MAC complementa permissoes tradicionais (DAC)", "SIM"],
            ["3. Alteracoes de politica avaliadas/registradas", "SIM"],
            ["4. Estado operacional validado antes de producao", "SIM"],
            ["5. Processos criticos sob politica MAC", "SIM"],
            ["6. Verificacoes com evidencias", "SIM"],
            ["7. Nenhuma config alterada sem validacao", "SIM"],
            ["8. Observacoes da configuracao registradas", "SIM"],
            ["9. MAC integra politica permanente de Hardening", "SIM"],
            ["10. Conclusoes subsidiam Lab 4B", "SIM"],
        ],
        st, [13.5*cm, 3.2*cm], OK
    ))
    story.append(kv([
        ("Resultado", "OS CONCLUIDA - camada MAC (SELinux Enforcing) validada no WEB-01"),
        ("Documento tecnico", "Lab04A_Mandatory_Access_Control_PREENCHIDO.pdf"),
        ("Equipe", TEAM),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 04A - Ordem de Servico"),
              onLaterPages=footer("Lab 04A - Ordem de Servico"))
    print("OS OK")


def build_lab(paths):
    st = styles()
    doc = SimpleDocTemplate(str(OUT_LAB), pagesize=A4,
                            leftMargin=1.4*cm, rightMargin=1.4*cm,
                            topMargin=1.6*cm, bottomMargin=1.6*cm,
                            title="Lab 04A - Mandatory Access Control", author=TEAM)
    story = []
    story.append(Paragraph("AMAZONTECH - Gerencia de Infraestrutura e Seguranca", st["CoverSub"]))
    story.append(Paragraph("RELATORIO TECNICO - Laboratorio 04A", st["CoverTitle"]))
    story.append(Paragraph("Validacao da Camada Mandatory Access Control (MAC)", st["CoverSub"]))
    story.append(Paragraph(f"<b>Equipe:</b> {TEAM}", st["Meta"]))
    story.append(Paragraph(
        f"Curso: Windows e Linux Hardening | Disciplina: Hardening Linux | Data: {DATE}",
        st["Meta"]))
    story.append(Paragraph(
        "AmazonTech | WEB-01 | Debian 13.6 | SELinux Enforcing | Politica default",
        st["Meta"]))
    story.append(hr())

    story.append(Paragraph("1. Objetivo da Atividade", st["H1"]))
    story.append(Paragraph(
        "Validar a camada Mandatory Access Control do servidor WEB-01 antes da entrada em producao: "
        "identificar SELinux ou AppArmor, verificar estado operacional, interpretar contextos/perfis "
        "e emitir parecer comparativo. O objetivo corporativo e impedir que processos autorizados "
        "executem acoes alem da politica, mesmo apos exploracao de vulnerabilidades em aplicacoes.",
        st["Body"]))

    story.append(Paragraph("2. Caracterizacao do Ambiente", st["H1"]))
    story.append(kv([
        ("Distribuicao Linux", "Debian GNU/Linux 13 (trixie)"),
        ("Versao", "13.6 / kernel 6.6.114.1-microsoft-standard-WSL2"),
        ("Maquina / hostname", "WEB-01 / MachadoPC"),
        ("LSM do kernel", "capability,landlock,yama,safesetid,selinux"),
        ("Data da atividade", DATE),
        ("Responsavel pela execucao", TEAM),
    ], st))

    story.append(Paragraph("3. Identificacao do mecanismo MAC", st["H1"]))
    story.append(Paragraph(
        "<b>[X] SELinux</b> &nbsp;&nbsp; [ ] AppArmor &nbsp;&nbsp; [ ] Outro<br/>"
        "<b>Justificativa:</b> O LSM do kernel lista <b>selinux</b> (nao apparmor). Pacotes "
        "selinux-utils, policycoreutils, selinux-policy-default e semanage-utils instalados. "
        "sestatus=enabled, getenforce=Enforcing, politica <b>default</b> carregada. Labels reais "
        "em arquivos (etc_t, shadow_t, sshd_exec_t, httpd_sys_content_t). AppArmor permanece "
        "instalado em user-space apenas para o bloco comparativo do laboratorio.",
        st["Body"]))
    story.append(shot(paths, "01_ambiente", st))
    story.append(PageBreak())
    story.append(shot(paths, "02_sestatus_getenforce", st))

    story.append(Paragraph("4. Resultados obtidos", st["H1"]))
    story.append(Paragraph("4.1 Verificacao inicial", st["H2"]))
    story.append(grid(
        ["Verificacao", "Resultado encontrado"],
        [
            ["Mecanismo identificado", "SELinux"],
            ["Estado operacional", "enabled / Enforcing"],
            ["Politica carregada", "default"],
            ["Perfis AppArmor", "N/A (MAC ativo = SELinux); AA user-space para comparacao"],
            ["Ferramenta de validacao", "sestatus + getenforce"],
        ],
        st, [5.5*cm, 11.2*cm]
    ))

    story.append(Paragraph("4.2 Ferramentas utilizadas", st["H2"]))
    story.append(grid(
        ["Ferramenta", "Finalidade", "Resultado obtido"],
        [
            ["sestatus", "Resumo SELinux", "enabled; policy default; mode Enforcing"],
            ["getenforce", "Modo atual", "Enforcing (coerente com sestatus)"],
            ["ls -Z", "Contextos de arquivos", "etc_t, shadow_t, sshd_exec_t, httpd_sys_content_t"],
            ["ps -Z", "Dominios de processos", "system_u:system_r:kernel_t:s0 (contextos SELinux)"],
            ["restorecon", "Restaurar labels", "motd: user_home_t -> etc_t; /var/www -> httpd_sys_content_t"],
            ["semanage", "Consultar fcontext", "5843 regras; politicas httpd/sshd distintas"],
            ["aa-status", "Resumo AppArmor", "AA nao e o LSM ativo; analisado para comparativo"],
            ["aa-enforce/complain", "Modos de perfil AA", "Ferramentas disponiveis; interpretadas"],
            ["aa-logprof/genprof", "Evolucao de perfis AA", "Interpretadas (menor privilegio)"],
        ],
        st, [3.2*cm, 4.5*cm, 9.0*cm]
    ))

    story.append(PageBreak())
    story.append(Paragraph("5. Evidencias coletadas", st["H1"]))
    story.append(shot(paths, "03_ls_Z", st))
    story.append(PageBreak())
    story.append(shot(paths, "04_ps_Z", st))
    story.append(shot(paths, "05_restorecon", st))
    story.append(PageBreak())
    story.append(shot(paths, "06_semanage", st))
    story.append(shot(paths, "07_apparmor_comparativo", st))

    story.append(Paragraph("Exercicios SELinux - respostas", st["H2"]))
    story.append(Paragraph(
        "<b>Ex.1 sestatus:</b> status enabled; modo Enforcing; politica default.<br/>"
        "<b>Ex.2 getenforce:</b> Enforcing. Coerente com sestatus (Current mode / Mode from config).<br/>"
        "<b>Ex.3 ls -Z:</b> Sim, apresenta contexto alem do ls -l. Exemplos: /etc/passwd=etc_t; "
        "/etc/shadow=shadow_t; /usr/sbin/sshd=sshd_exec_t; /var/www/html/index.html=httpd_sys_content_t. "
        "O Type e o campo decisivo. Nem todos os arquivos compartilham o mesmo Type — isso permite "
        "isolamento por funcao.<br/>"
        "<b>Ex.4 ps -Z:</b> Processos com LABEL SELinux (system_u:system_r:kernel_t:s0). A separacao "
        "por dominio limita o que um processo comprometido pode fazer, mesmo sob o mesmo UID DAC.<br/>"
        "<b>Ex.5 restorecon:</b> Demonstrado em /etc/motd (chcon user_home_t -> restorecon etc_t) e "
        "em /var/www/html (httpd_sys_content_t). Sem o label correto, servicos legitimos podem falhar "
        "ou politicas deixam de proteger o recurso.<br/>"
        "<b>Ex.6 semanage fcontext -l:</b> 5843 regras; nao se restringem a um unico diretorio; "
        "httpd/sshd possuem padroes proprios. Politica generica unica violaria menor privilegio e "
        "isolamento.",
        st["Body"]))

    story.append(Paragraph("Exercicios AppArmor - respostas (comparativo)", st["H2"]))
    story.append(Paragraph(
        "<b>Ex.7-11:</b> Pacotes AppArmor e ferramentas (aa-status, aa-enforce, aa-complain, "
        "aa-logprof, aa-genprof) instalados e interpretados. Neste kernel o LSM ativo e SELinux; "
        "portanto o MAC operacional do WEB-01 e SELinux. Conceitos Enforce/Complain equivalem, "
        "em espirito, a Enforcing/Permissive do SELinux. aa-logprof/genprof apoiam evolucao "
        "gradual de perfis sob menor privilegio — analogos a ajuste de politica SELinux.",
        st["Body"]))

    story.append(PageBreak())
    story.append(Paragraph("6. Comparacao entre SELinux e AppArmor", st["H1"]))
    story.append(grid(
        ["Aspecto", "SELinux", "AppArmor"],
        [
            ["Filosofia / modelo", "Labels/contextos (Type Enforcement)", "Perfis por caminho de programa"],
            ["Unidade principal", "Type/domain (httpd_t, etc_t)", "Perfil do binario"],
            ["Facilidade inicial", "Mais complexa (rotulagem ampla)", "Mais intuitiva (path-based)"],
            ["Flexibilidade", "Alta (fcontext + modulos)", "Alta por aplicacao"],
            ["Ferramentas do lab", "sestatus, getenforce, ls -Z, ps -Z, restorecon, semanage",
             "aa-status, aa-enforce, aa-complain, aa-logprof, aa-genprof"],
            ["Distros comuns", "Rocky, Alma, RHEL (+ kernels com LSM SELinux)", "Ubuntu, Debian (tipico)"],
            ["Neste WEB-01", "MAC ATIVO (Enforcing)", "User-space para estudo comparativo"],
        ],
        st, [3.2*cm, 6.75*cm, 6.75*cm]
    ))

    story.append(Paragraph("7. Discussao Tecnica", st["H1"]))
    story.append(Paragraph(
        "<b>1. MAC complementa DAC?</b> Sim. DAC define quem acessa; MAC define o que o processo "
        "pode fazer mesmo autorizado, reduzindo impacto de apps comprometidas.<br/>"
        "<b>2. Diferencas:</b> SELinux rotula objetos/processos; AppArmor associa perfil ao path. "
        "No WEB-01, SELinux esta operacional com labels e politica default.<br/>"
        "<b>3. Mais intuitivo:</b> AppArmor costuma ser mais direto para iniciantes; SELinux oferece "
        "controle mais fino via Types — adequado a hardening corporativo exigente.<br/>"
        "<b>4. Evidencias de config correta:</b> sestatus enabled + Enforcing; getenforce coerente; "
        "labels em arquivos criticos; restorecon funcional; 5843 regras semanage.<br/>"
        "<b>5. MAC elimina DAC?</b> Nao. Sao camadas complementares (defesa em profundidade).<br/>"
        "<b>Discussao isolamento:</b> Mesmas permissoes para todas as apps quebrariam isolamento, "
        "menor privilegio e contencao de incidentes.",
        st["Body"]))

    story.append(Paragraph("8. Parecer Tecnico da Equipe", st["H1"]))
    story.append(hr())
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Servidor", "WEB-01"),
        ("Mecanismo", "SELinux"),
        ("Estado", "enabled / Enforcing / policy default"),
        ("Data", DATE),
        ("Equipe", TEAM),
    ], st))
    story.append(Paragraph(
        "<b>Beneficios:</b> camada MAC restringe processos alem do DAC; Type Enforcement isola "
        "dominios; restorecon e semanage permitem manter labels e politicas consistentes.<br/>"
        "<b>Evidencias:</b> sestatus/getenforce Enforcing; ls -Z com Types corretos; restorecon "
        "restaurando motd e conteudo httpd; semanage com milhares de regras especificas por servico.<br/>"
        "<b>Recomendacao final:</b> [X] <b>APTO PARA OPERACAO</b> sob o ponto de vista da camada "
        "Mandatory Access Control. O WEB-01 opera com SELinux habilitado, politica default carregada "
        "e modo Enforcing validado, integrando o MAC a politica permanente de Hardening da AmazonTech.<br/>"
        "<b>Responsavel tecnico:</b> " + TEAM + f"<br/><b>Data:</b> {DATE}",
        st["Body"]))

    story.append(Paragraph("9. Conclusoes", st["H1"]))
    story.append(Paragraph(
        "A equipe validou a camada MAC do WEB-01 com SELinux em Enforcing. Contextos de arquivos e "
        "processos, restauracao de labels e consulta de politicas foram exercitados com evidencias. "
        "AppArmor foi analisado comparativamente. MAC nao substitui DAC: complementa o Hardening. "
        "Proxima etapa: Lab 4B (manutencao continua, patches, monitoramento e auditoria).",
        st["Body"]))

    story.append(Paragraph("Checklist Final", st["H2"]))
    story.append(grid(
        ["Item", "OK?"],
        [
            ["Ambiente e distro identificados", "SIM"],
            ["Mecanismo MAC identificado (SELinux)", "SIM"],
            ["Estado operacional Enforcing validado", "SIM"],
            ["Exercicios SELinux com evidencias", "SIM"],
            ["Bloco AppArmor comparativo", "SIM"],
            ["Tabela comparativa SELinux x AppArmor", "SIM"],
            ["Parecer tecnico APTO + screenshots", "SIM"],
        ],
        st, [14.0*cm, 2.7*cm], OK
    ))
    story.append(Paragraph(
        "Screenshots: lab04a/evidencias/shots/img/ | Raw: lab04a/evidencias/raw/",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 04A - MAC + Screenshots"),
              onLaterPages=footer("Lab 04A - MAC + Screenshots"))
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
