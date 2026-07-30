#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os dois PDFs de entrega do Lab 02."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)

PRIMARY = HexColor("#1a365d")
ACCENT = HexColor("#2c5282")
LIGHT = HexColor("#edf2f7")
OK = HexColor("#276749")
WARN = HexColor("#c05621")
BORDER = HexColor("#cbd5e0")

BASE = r"d:\MMB\workspace\hardening\lab02"
OUT_OS = BASE + r"\entregaveis\Lab02_Ordem_de_Servico_PREENCHIDO.pdf"
OUT_LAB = BASE + r"\entregaveis\Lab02_Identidades_e_Privilegios_PREENCHIDO.pdf"
DL_OS = r"c:\Users\marge\Downloads\Lab02_Ordem_de_Servico_PREENCHIDO.pdf"
DL_LAB = r"c:\Users\marge\Downloads\Lab02_Identidades_e_Privilegios_PREENCHIDO.pdf"


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=16,
                         textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=8, leading=20))
    s.add(ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=11,
                         textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4, leading=14))
    s.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=12,
                         textColor=PRIMARY, spaceBefore=10, spaceAfter=6, leading=15))
    s.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=10,
                         textColor=ACCENT, spaceBefore=8, spaceAfter=4, leading=13))
    s.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=9,
                         alignment=TA_JUSTIFY, spaceAfter=5, leading=12))
    s.add(ParagraphStyle("Left", fontName="Helvetica", fontSize=9,
                         alignment=TA_LEFT, spaceAfter=3, leading=12))
    s.add(ParagraphStyle("Mono", fontName="Courier", fontSize=7.5,
                         textColor=HexColor("#1a202c"), backColor=LIGHT,
                         leftIndent=2, rightIndent=2, spaceBefore=2, spaceAfter=4, leading=9.5))
    s.add(ParagraphStyle("Meta", fontName="Helvetica", fontSize=9,
                         textColor=HexColor("#4a5568"), alignment=TA_CENTER, spaceAfter=2))
    s.add(ParagraphStyle("Small", fontName="Helvetica", fontSize=8,
                         textColor=HexColor("#4a5568"), alignment=TA_JUSTIFY, spaceAfter=3, leading=10))
    s.add(ParagraphStyle("Q", fontName="Helvetica-Bold", fontSize=9,
                         textColor=PRIMARY, spaceBefore=5, spaceAfter=2, leading=11))
    s.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=7.5, leading=9.5))
    s.add(ParagraphStyle("Head", fontName="Helvetica-Bold", fontSize=7.5,
                         textColor=white, leading=9.5))
    return s


def footer(title):
    def _f(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(PRIMARY)
        canvas.setLineWidth(1)
        canvas.line(1.6*cm, A4[1]-1.2*cm, A4[0]-1.6*cm, A4[1]-1.2*cm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(ACCENT)
        canvas.drawString(1.6*cm, A4[1]-1.05*cm, title)
        canvas.drawRightString(A4[0]-1.6*cm, A4[1]-1.05*cm, "AmazonTech — WEB-01")
        canvas.line(1.6*cm, 1.3*cm, A4[0]-1.6*cm, 1.3*cm)
        canvas.drawCentredString(A4[0]/2, 0.85*cm, f"Página {doc.page} | 28/07/2026 | Evidências coletadas em Debian 13 (MachadoPC)")
        canvas.restoreState()
    return _f


def kv(rows, st, c1=4.5*cm, c2=12.2*cm):
    data = [[Paragraph(f"<b>{k}</b>", st["Cell"]), Paragraph(str(v), st["Cell"])] for k, v in rows]
    t = Table(data, colWidths=[c1, c2])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def grid(headers, rows, st, widths, head_color=PRIMARY):
    data = [[Paragraph(h, st["Head"]) for h in headers]]
    for r in rows:
        data.append([Paragraph(str(c), st["Cell"]) for c in r])
    t = Table(data, colWidths=widths)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), head_color),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
    ]
    t.setStyle(TableStyle(style))
    return t


def hr():
    return HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6)


# ===================== PDF 1: ORDEM DE SERVICO =====================
def build_ordem_servico():
    st = styles()
    doc = SimpleDocTemplate(OUT_OS, pagesize=A4,
                            leftMargin=1.6*cm, rightMargin=1.6*cm,
                            topMargin=1.7*cm, bottomMargin=1.8*cm,
                            title="Lab 02 - Ordem de Serviço (Preenchido)",
                            author="Equipe Segurança AmazonTech")
    story = []
    story.append(Paragraph("DOCUMENTO DE ABERTURA E ENCERRAMENTO", st["CoverSub"]))
    story.append(Paragraph("Ordem de Serviço — Laboratório 02", st["CoverTitle"]))
    story.append(Paragraph("Controle de Identidades e Privilégios Administrativos", st["CoverSub"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(hr())

    story.append(Paragraph("1. Identificação da Atividade", st["H1"]))
    story.append(kv([
        ("Empresa simulada", "AmazonTech"),
        ("Unidade responsável", "Gerência de Infraestrutura e Segurança da Informação"),
        ("Servidor analisado", "WEB-01 (hostname operacional: MachadoPC)"),
        ("Sistema operacional", "Debian GNU/Linux 13 (trixie) — versão 13.6"),
        ("Área técnica", "Administração e Hardening de Sistemas Linux"),
        ("Tipo de atividade", "Auditoria, correção e validação de controles de acesso"),
        ("Modalidade", "Laboratório prático"),
        ("Execução", "Individual / equipe técnica de hardening"),
        ("Tempo estimado", "2 a 3 horas"),
        ("Data de execução", "28/07/2026"),
        ("Responsável pela execução", "Equipe de Segurança — analista(s) designado(s)"),
        ("Status da OS", "<b>CONCLUÍDA</b> — correções aplicadas e validadas com evidências"),
    ], st))

    story.append(Paragraph("2. Ordem de Serviço — Aceite e Escopo", st["H1"]))
    story.append(Paragraph(
        "A Gerência de Infraestrutura e Segurança da Informação da AmazonTech identificou "
        "fragilidades no controle de identidades e privilégios administrativos do servidor WEB-01. "
        "A equipe técnica aceitou a OS e executou auditoria, correção e validação conforme a "
        "política corporativa (menor privilégio, segregação de funções, rastreabilidade e necessidade de acesso).",
        st["Body"]))

    story.append(Paragraph("3. Problemas Relatados × Tratamento", st["H1"]))
    story.append(grid(
        ["Problema relatado", "Situação encontrada", "Ação executada", "Status"],
        [
            ["Ausência de inventário atualizado", "Inventário inicial sem usuários corporativos da OS", "Inventário completo + criação das identidades", "Resolvido"],
            ["Contas sem função identificada", "Ambiente sem ana/carlos/maria/paulo/temporario", "Contas criadas e classificadas", "Resolvido"],
            ["Associação inadequada a grupos", "ana∈infraestrutura; maria∈desenvolvimento", "Associações indevidas removidas", "Resolvido"],
            ["Excesso de contas administrativas", "sudo: machado,carlos,ana,backup,temporario", "sudo final: machado,carlos", "Resolvido"],
            ["Contas de serviço incompatíveis", "backup temporariamente no sudo", "Removido do sudo; shell nologin", "Resolvido"],
            ["Permissões excessivas em diretórios", "Diretórios corporativos inexistentes/inconsistentes", "Criados com 750/770 e donos corretos", "Resolvido"],
            ["Ausência de controle excepcional", "Sem ACL para auditoria financeira", "ACL temporária u:paulo:rx testada e removida", "Resolvido"],
            ["Uso inadequado da conta root", "Risco de uso rotineiro de root", "Política sudo validada; admin via carlos/machado", "Resolvido"],
            ["Falta de revisão periódica", "Sem processo documentado", "Checklist + parecer + plano de revisão", "Tratado"],
        ],
        st, [4.0*cm, 4.2*cm, 4.5*cm, 2.0*cm], WARN
    ))

    story.append(Paragraph("4. Objetivo Geral — Cumprimento", st["H1"]))
    story.append(Paragraph(
        "Foi revisado e fortalecido o controle de identidades, grupos, permissões e privilégios "
        "administrativos do servidor Linux da AmazonTech, com evidências de conformidade final "
        "registradas em 28/07/2026.",
        st["Body"]))

    story.append(Paragraph("5. Objetivos Específicos — Checklist de Cumprimento", st["H1"]))
    story.append(grid(
        ["Objetivo específico", "Cumprido?"],
        [
            ["Identificar usuários e grupos existentes", "☑ Sim"],
            ["Classificar contas (usuário / administrativa / serviço / temporária)", "☑ Sim"],
            ["Organizar usuários conforme funções", "☑ Sim"],
            ["Remover associações incompatíveis", "☑ Sim"],
            ["Revisar integrantes dos grupos administrativos", "☑ Sim"],
            ["Bloquear contas sem necessidade operacional", "☑ Sim (temporario)"],
            ["Configurar proprietários e grupos dos diretórios", "☑ Sim"],
            ["Aplicar permissões tradicionais Linux", "☑ Sim (750/770)"],
            ["Conceder acessos excepcionais por ACL", "☑ Sim (teste paulo)"],
            ["Revisar política de uso do sudo", "☑ Sim"],
            ["Testar acessos autorizados e não autorizados", "☑ Sim"],
            ["Produzir parecer técnico", "☑ Sim (Doc. Identidades)"],
        ],
        st, [13.5*cm, 3.2*cm], OK
    ))

    story.append(PageBreak())
    story.append(Paragraph("6. Identidades, Grupos e Diretórios — Estado Final", st["H1"]))
    story.append(Paragraph("Identidades do ambiente (conforme OS)", st["H2"]))
    story.append(grid(
        ["Usuário", "Função", "Classificação", "Estado final"],
        [
            ["ana", "Desenvolvedora", "Conta de usuário", "∈ desenvolvimento; sem sudo"],
            ["carlos", "Admin. infraestrutura", "Conta administrativa", "∈ infraestrutura + sudo"],
            ["maria", "Analista financeira", "Conta de usuário", "∈ financeiro; sem sudo"],
            ["paulo", "Auditor interno", "Conta de usuário", "∈ auditoria; sem sudo"],
            ["backup", "Rotinas de cópia", "Conta de serviço", "nologin; fora do sudo"],
            ["temporario", "Prestador (projeto encerrado)", "Conta temporária", "Bloqueada (passwd -l)"],
            ["machado", "Operador do laboratório", "Conta administrativa", "∈ sudo (execução do lab)"],
        ],
        st, [2.5*cm, 4.0*cm, 3.5*cm, 6.7*cm]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Diretórios corporativos", st["H2"]))
    story.append(grid(
        ["Diretório", "Proprietário", "Grupo", "Permissão", "Conformidade"],
        [
            ["/projetos", "ana", "desenvolvimento", "750", "☑"],
            ["/financeiro", "maria", "financeiro", "770", "☑"],
            ["/auditoria", "paulo", "auditoria", "750", "☑"],
            ["/infraestrutura", "carlos", "infraestrutura", "750", "☑"],
        ],
        st, [3.5*cm, 2.8*cm, 3.5*cm, 2.5*cm, 2.4*cm], OK
    ))

    story.append(Paragraph("7. Conformidade com a Política de Segurança", st["H1"]))
    story.append(grid(
        ["Diretriz (resumo)", "Atendida?"],
        [
            ["1. Conta individual por pessoa", "☑"],
            ["2. Evitar contas compartilhadas", "☑"],
            ["3. Pertencer apenas a grupos necessários", "☑"],
            ["4. Acesso administrativo restrito", "☑ (carlos, machado)"],
            ["5. Conta de serviço sem login interativo", "☑ (backup → nologin)"],
            ["6. Contas de projeto encerrado bloqueadas", "☑ (temporario)"],
            ["7. Acesso a diretórios por grupos", "☑"],
            ["8. Evitar permissões para outros (o)", "☑ (o=---)"],
            ["9. Não utilizar 777", "☑"],
            ["10. Exceções via ACL quando apropriado", "☑ (teste e remoção)"],
            ["11. Evitar uso rotineiro de root", "☑ (política sudo)"],
            ["12. Atividades administrativas via sudo", "☑"],
            ["13. Validação após alterações", "☑"],
            ["14. Registro de evidências", "☑ (evidencias/lab02_evidence.txt)"],
        ],
        st, [13.5*cm, 3.2*cm], OK
    ))

    story.append(Paragraph("8. Entregáveis Vinculados a esta OS", st["H1"]))
    story.append(Paragraph(
        "1. Inventário de usuários e grupos<br/>"
        "2. Relação das inconsistências encontradas<br/>"
        "3. Registro das correções realizadas<br/>"
        "4. Evidências dos testes de acesso<br/>"
        "5. Checklist final de segurança<br/>"
        "6. Parecer técnico sobre o ambiente<br/><br/>"
        "Documento técnico detalhado: <b>Lab02_Identidades_e_Privilegios_PREENCHIDO.pdf</b>",
        st["Left"]))

    story.append(Paragraph("9. Encerramento da Ordem de Serviço", st["H1"]))
    story.append(Paragraph(
        "Com base nas evidências técnicas, a OS é encerrada como <b>CONCLUÍDA COM RESSALVAS OPERACIONAIS MENORES</b>: "
        "os controles de identidade e privilégio solicitados foram implementados e validados. "
        "Ressalvas: manter revisão periódica de sudo/ACL; avaliar se a conta machado deve permanecer "
        "como admin permanente no WEB-01 de produção; reforçar logging de autenticação.",
        st["Body"]))
    story.append(kv([
        ("Resultado da OS", "Concluída — ambiente apto com ressalvas"),
        ("Data de encerramento", "28/07/2026"),
        ("Evidência bruta", "evidencias/lab02_evidence.txt"),
        ("Assinatura técnica", "Equipe de Hardening / Segurança da Informação"),
    ], st))

    doc.build(story, onFirstPage=footer("Lab 02 — Ordem de Serviço (Preenchida)"),
              onLaterPages=footer("Lab 02 — Ordem de Serviço (Preenchida)"))
    print("OS:", OUT_OS)


# ===================== PDF 2: LAB IDENTIDADES =====================
def build_lab_identidades():
    st = styles()
    doc = SimpleDocTemplate(OUT_LAB, pagesize=A4,
                            leftMargin=1.6*cm, rightMargin=1.6*cm,
                            topMargin=1.7*cm, bottomMargin=1.8*cm,
                            title="Lab 02 - Identidades e Privilégios (Preenchido)",
                            author="Equipe Segurança AmazonTech")
    story = []

    story.append(Paragraph("LABORATÓRIO 2 — RELATÓRIO TÉCNICO COMPLETO", st["CoverSub"]))
    story.append(Paragraph("Controle de Identidades e Privilégios Administrativos", st["CoverTitle"]))
    story.append(Paragraph("Windows e Linux Hardening — Aula 2", st["CoverSub"]))
    story.append(Spacer(1, 0.15*cm))
    story.append(hr())
    story.append(Paragraph(
        "Empresa: AmazonTech | Servidor: WEB-01 | SO: Debian 13.6 (trixie) | Data: 28/07/2026 | "
        "Hostname: MachadoPC",
        st["Meta"]))
    story.append(Paragraph(
        "Este documento responde às 7 missões do laboratório, com inventário, inconsistências, "
        "correções, testes, checklist e parecer técnico. Evidências: saída de terminal em evidencias/lab02_evidence.txt.",
        st["Body"]))

    # ---- MISSAO 1 ----
    story.append(Paragraph("Missão 1 — Inventário das Identidades", st["H1"]))
    story.append(hr())
    story.append(Paragraph("Atividades 1–3 — Usuários, grupos e amostragem", st["H2"]))
    story.append(grid(
        ["Usuário", "UID", "Shell", "Classificação"],
        [
            ["root", "0", "/bin/bash", "Administrativa (sistema)"],
            ["machado", "1000", "/bin/bash", "Administrativa (lab/sudo)"],
            ["ana", "1001", "/bin/bash", "Conta de usuário"],
            ["carlos", "1002", "/bin/bash", "Conta administrativa"],
            ["maria", "1003", "/bin/bash", "Conta de usuário"],
            ["paulo", "1004", "/bin/bash", "Conta de usuário"],
            ["temporario", "1005", "/bin/bash", "Conta temporária"],
            ["backup", "34", "/usr/sbin/nologin", "Conta de serviço"],
            ["www-data, _apt, daemon...", "sistema", "nologin/false", "Contas de serviço"],
        ],
        st, [3.0*cm, 1.8*cm, 3.5*cm, 6.4*cm]
    ))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "<b>Grupos corporativos:</b> desenvolvimento (1001), infraestrutura (1002), financeiro (1003), "
        "auditoria (1004) — <i>criados nesta missão/missão 2</i>. Grupo sudo (27) já existia.",
        st["Left"]))
    story.append(Paragraph("Amostra id (situação após criação / antes das correções finais):", st["Left"]))
    story.append(Paragraph(
        "ana: uid=1001 groups=ana,sudo,desenvolvimento,infraestrutura<br/>"
        "carlos: uid=1002 groups=carlos,sudo,infraestrutura<br/>"
        "maria: uid=1003 groups=maria,desenvolvimento,financeiro",
        st["Mono"]))

    story.append(Paragraph("Atividade 4–5 — Classificação e inconsistências", st["H2"]))
    story.append(grid(
        ["Inconsistência", "Evidência", "Risco"],
        [
            ["ana ∈ sudo e infraestrutura", "id ana (antes)", "Privilégio excessivo / segregação violada"],
            ["maria ∈ desenvolvimento", "id maria (antes)", "Acesso a área incompatível"],
            ["backup ∈ sudo", "getent group sudo", "Conta de serviço privilegiada"],
            ["temporario ∈ sudo", "getent group sudo", "Prestador encerrado ainda admin"],
            ["Excesso no grupo sudo", "machado,carlos,ana,backup,temporario", "Superfície de ataque ampliada"],
            ["Diretórios corporativos ausentes", "ls /projetos etc. inexistentes", "Sem segregação de dados"],
        ],
        st, [4.5*cm, 5.5*cm, 6.7*cm], WARN
    ))

    story.append(Paragraph("Reflexão — Missão 1", st["H2"]))
    story.append(Paragraph(
        "<b>1.</b> Nem todos eram necessários no estado inicial: faltavam identidades corporativas e "
        "havia contas privilegiadas sem alinhamento à função.<br/>"
        "<b>2.</b> Merecem investigação: backup no sudo, temporario privilegiado e ana com admin.<br/>"
        "<b>3.</b> Sim — indícios claros de violação do menor privilégio.<br/>"
        "<b>4.</b> Antes das correções, o ambiente <b>não</b> aparentava política organizada de identidades.",
        st["Body"]))

    # ---- MISSAO 2 ----
    story.append(PageBreak())
    story.append(Paragraph("Missão 2 — Organização de Usuários e Grupos", st["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Grupos verificados via getent: nenhum corporativo existia → todos criados com groupadd. "
        "Associações aplicadas com usermod -aG; remoções com gpasswd -d.",
        st["Body"]))
    story.append(grid(
        ["Usuário", "Grupo anterior (inconsistente)", "Grupo final", "Decisão", "Justificativa"],
        [
            ["ana", "desenvolvimento, infraestrutura, sudo", "desenvolvimento", "Remover infraestrutura/sudo", "Dev não exige admin do servidor"],
            ["carlos", "infraestrutura, sudo", "infraestrutura, sudo", "Manter", "Admin de infraestrutura autorizado"],
            ["maria", "desenvolvimento, financeiro", "financeiro", "Remover desenvolvimento", "Financeiro não atua em código"],
            ["paulo", "auditoria", "auditoria", "Manter", "Função de auditor"],
            ["backup", "sudo", "sem grupo admin", "Remover sudo", "Serviço com privilégio mínimo"],
        ],
        st, [2.0*cm, 4.2*cm, 3.0*cm, 3.0*cm, 4.5*cm]
    ))
    story.append(Paragraph("Composição final dos grupos:", st["Left"]))
    story.append(Paragraph(
        "desenvolvimento:x:1001:ana<br/>"
        "infraestrutura:x:1002:carlos<br/>"
        "financeiro:x:1003:maria<br/>"
        "auditoria:x:1004:paulo",
        st["Mono"]))
    story.append(Paragraph("Reflexão — Missão 2", st["H2"]))
    story.append(Paragraph(
        "<b>1.</b> Grupos simplificam concessão/revogação e evitam permissões individuais espalhadas.<br/>"
        "<b>2.</b> Grupos incompatíveis geram vazamento de dados e quebra de segregação.<br/>"
        "<b>3.</b> Conta de serviço <b>não</b> deve pertencer a grupo administrativo sem justificativa formal.<br/>"
        "<b>4.</b> Associação deve ser <b>revisada periodicamente</b>, não tratada como permanente.",
        st["Body"]))

    # ---- MISSAO 3 ----
    story.append(Paragraph("Missão 3 — Revisão dos Privilégios Administrativos", st["H1"]))
    story.append(hr())
    story.append(grid(
        ["Identidade", "Classificação", "Decisão", "Justificativa"],
        [
            ["carlos", "Privilégio compatível", "Manter no sudo", "Administrador de infraestrutura"],
            ["ana", "Privilégio excessivo", "Remover do sudo", "Desenvolvimento não exige admin ampla"],
            ["backup", "Privilégio excessivo", "Remover do sudo", "Serviço com menor privilégio"],
            ["temporario", "Deve ser bloqueada", "Remover sudo + passwd -l", "Projeto encerrado"],
            ["machado", "Admin do laboratório", "Manter", "Operador responsável pela execução"],
        ],
        st, [2.5*cm, 3.5*cm, 3.5*cm, 7.2*cm]
    ))
    story.append(Paragraph("Evidências:", st["Left"]))
    story.append(Paragraph(
        "sudo ANTES: machado,carlos,ana,backup,temporario<br/>"
        "sudo DEPOIS: machado,carlos<br/>"
        "temporario: passwd -S → L (locked) 2026-07-28<br/>"
        "backup: /usr/sbin/nologin",
        st["Mono"]))
    story.append(Paragraph("Reflexão — Missão 3", st["H2"]))
    story.append(Paragraph(
        "<b>1.</b> Não — admin de área ≠ acesso irrestrito ao SO.<br/>"
        "<b>2.</b> Conta de serviço privilegiada, se comprometida, concede poder administrativo imediato.<br/>"
        "<b>3.</b> Remover privilégio tira poder; bloquear conta impede autenticação/uso da identidade.<br/>"
        "<b>4.</b> Revisões periódicas detectam drift (projetos encerrados, mudanças de função).",
        st["Body"]))

    # ---- MISSAO 4 ----
    story.append(PageBreak())
    story.append(Paragraph("Missão 4 — Propriedade e Permissões", st["H1"]))
    story.append(hr())
    story.append(grid(
        ["Diretório", "Proprietário", "Grupo", "Permissão", "Resultado"],
        [
            ["/projetos", "ana", "desenvolvimento", "750 (rwxr-x---)", "Acesso restrito à área"],
            ["/financeiro", "maria", "financeiro", "770 (rwxrwx---)", "Grupo autorizado a gravar"],
            ["/auditoria", "paulo", "auditoria", "750", "Outros sem acesso"],
            ["/infraestrutura", "carlos", "infraestrutura", "750", "Acesso controlado"],
        ],
        st, [3.2*cm, 2.5*cm, 3.5*cm, 3.8*cm, 3.7*cm], OK
    ))
    story.append(Paragraph("ls -ld (evidência):", st["Left"]))
    story.append(Paragraph(
        "drwxr-x--- 2 ana    desenvolvimento 4096 Jul 28 19:00 /projetos<br/>"
        "drwxrwx--- 2 maria  financeiro      4096 Jul 28 19:00 /financeiro<br/>"
        "drwxr-x--- 2 paulo  auditoria       4096 Jul 28 19:00 /auditoria<br/>"
        "drwxr-x--- 2 carlos infraestrutura  4096 Jul 28 19:00 /infraestrutura",
        st["Mono"]))
    story.append(Paragraph("Testes de acesso", st["H2"]))
    story.append(grid(
        ["Teste", "Esperado", "Obtido"],
        [
            ["sudo -u ana ls /projetos", "Permitido", "OK"],
            ["sudo -u maria ls /financeiro", "Permitido", "OK"],
            ["sudo -u paulo ls /auditoria", "Permitido", "OK"],
            ["sudo -u carlos ls /infraestrutura", "Permitido", "OK"],
            ["sudo -u ana ls /financeiro", "Permission denied", "Permission denied"],
            ["sudo -u maria ls /infraestrutura", "Permission denied", "Permission denied"],
            ["sudo -u paulo ls /projetos", "Permission denied", "Permission denied"],
        ],
        st, [6.5*cm, 4.5*cm, 5.7*cm]
    ))
    story.append(Paragraph("Reflexão — Missão 4", st["H2"]))
    story.append(Paragraph(
        "<b>1.</b> 750 = grupo lê/acessa; 770 = grupo também grava.<br/>"
        "<b>2.</b> Financeiro exige colaboração de escrita entre membros da área.<br/>"
        "<b>3.</b> 777 permite qualquer usuário ler/alterar/apagar — risco crítico.<br/>"
        "<b>4.</b> Não — sem grupo/permissões corretas o controle fica incompleto.<br/>"
        "<b>5.</b> Grupos centralizam o acesso e reduzem gestão conta a conta.",
        st["Body"]))

    # ---- MISSAO 5 ----
    story.append(Paragraph("Missão 5 — ACL", st["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Pacote acl instalado. Concedido setfacl -m u:paulo:rx /financeiro; validado; depois removido com setfacl -x.",
        st["Body"]))
    story.append(grid(
        ["Teste", "Esperado", "Obtido"],
        [
            ["Listar /financeiro antes da ACL", "Negado", "Permission denied"],
            ["Listar após ACL", "Permitido", "Listagem OK"],
            ["Ler arquivo (com ACL no arquivo)", "Permitido", "Leitura OK"],
            ["Criar arquivo (touch)", "Negado", "Permission denied"],
            ["paulo ∈ financeiro?", "Não", "groups: apenas auditoria"],
            ["Listar após remover ACL", "Negado", "Permission denied"],
        ],
        st, [6.5*cm, 4.0*cm, 6.2*cm]
    ))
    story.append(Paragraph(
        "getfacl (com ACL): user:paulo:r-x · mask::rwx · ls -ld com símbolo +<br/>"
        "getfacl (após remoção): apenas user::/group::/other:: — sem entrada de paulo",
        st["Mono"]))
    story.append(Paragraph("Reflexão — Missão 5", st["H2"]))
    story.append(Paragraph(
        "<b>1.</b> Incluir paulo no financeiro tornaria o acesso permanente e excessivo (escrita potencial via 770).<br/>"
        "<b>2.</b> ACL permite exceção pontual sem alterar a estrutura organizacional.<br/>"
        "<b>3.</b> Em diretórios, x é necessário para atravessar/listar conforme política.<br/>"
        "<b>4.</b> A máscara limita as permissões efetivas das entradas ACL.<br/>"
        "<b>5.</b> Exceções esquecidas viram backdoors de acesso — devem ser removidas ao fim da necessidade.",
        st["Body"]))

    # ---- MISSAO 6 ----
    story.append(PageBreak())
    story.append(Paragraph("Missão 6 — Configuração e Validação do sudo", st["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Política observada em /etc/sudoers: root ALL=(ALL:ALL) ALL e %sudo ALL=(ALL:ALL) ALL; "
        "Defaults env_reset, mail_badpass, secure_path, use_pty. Nenhuma alteração indevida foi salva fora do escopo.",
        st["Body"]))
    story.append(grid(
        ["Usuário", "sudo -l -U", "Interpretação"],
        [
            ["carlos", "(ALL : ALL) ALL", "Administrador autorizado"],
            ["ana", "not allowed to run sudo", "Sem privilégio — correto"],
            ["maria", "not allowed to run sudo", "Sem privilégio — correto"],
            ["paulo", "not allowed to run sudo", "Sem privilégio — correto"],
            ["machado", "via %sudo", "Operador do laboratório"],
        ],
        st, [2.5*cm, 5.5*cm, 8.7*cm]
    ))
    story.append(Paragraph(
        "Teste administrativo: systemctl status cron → active (running).<br/>"
        "sudo -k: invalida o cache de timestamp; próximo sudo exige reautenticação — reduz janela de abuso se a sessão ficar desatendida.",
        st["Mono"]))
    story.append(Paragraph("Discussão técnica / Reflexão — Missão 6", st["H2"]))
    story.append(Paragraph(
        "<b>1.</b> sudo é preferível ao login root: identidade individual + logs.<br/>"
        "<b>2.</b> Conta própria garante responsabilização e rastreabilidade.<br/>"
        "<b>3.</b> Ações sudo podem ser auditadas (auth/journal), ao contrário do root compartilhado.<br/>"
        "<b>4.</b> Muitos membros em sudo ampliam drasticamente a superfície de ataque.",
        st["Body"]))

    # ---- MISSAO 7 ----
    story.append(Paragraph("Missão 7 — Auditoria Final + Parecer Técnico", st["H1"]))
    story.append(hr())
    story.append(Paragraph("Checklist Final de Segurança", st["H2"]))
    story.append(grid(
        ["Item", "Status"],
        [
            ["Usuários identificados e classificados", "☑"],
            ["Sem contas sem função conhecida (no escopo corporativo)", "☑"],
            ["Conta temporária bloqueada", "☑"],
            ["Conta de serviço sem shell interativa", "☑"],
            ["Grupos corporativos organizados", "☑"],
            ["Associações incompatíveis removidas", "☑"],
            ["Somente admins autorizados no sudo", "☑"],
            ["Diretórios com dono/grupo/permissões adequados", "☑"],
            ["Sem permissão 777", "☑"],
            ["Testes positivos e negativos registrados", "☑"],
            ["ACL excepcional testada e removida", "☑"],
            ["Política sudo consultada/validada", "☑"],
            ["Princípio do menor privilégio respeitado", "☑"],
            ["Evidências e parecer elaborados", "☑"],
        ],
        st, [13.5*cm, 3.2*cm], OK
    ))

    story.append(Paragraph("Parecer Técnico de Segurança", st["H2"]))
    story.append(kv([
        ("Empresa", "AmazonTech"),
        ("Servidor", "WEB-01 (MachadoPC)"),
        ("Responsável pela análise", "Equipe de Hardening / Segurança da Informação"),
        ("Data", "28/07/2026"),
    ], st))
    story.append(Paragraph(
        "<b>1. Objetivo.</b> Auditar e fortalecer identidades, grupos, permissões e privilégios administrativos.<br/><br/>"
        "<b>2. Situação inicial.</b> Ambiente sem estrutura corporativa de usuários/grupos/diretórios; "
        "após provisionamento do cenário, evidenciou-se excesso de sudo (ana, backup, temporario), "
        "associações cruzadas indevidas e ausência de segregação de dados.<br/><br/>"
        "<b>3. Inconsistências.</b> Privilégios excessivos; conta temporária ativa/privilegiada; "
        "conta de serviço no sudo; grupos incompatíveis; diretórios sem política; falta de controle excepcional via ACL.<br/><br/>"
        "<b>4. Correções.</b> Criação de grupos/usuários; remoção de associações indevidas; limpeza do sudo; "
        "bloqueio de temporario; nologin em backup; diretórios 750/770; testes ACL rx para paulo com remoção posterior; "
        "validação sudo -l.<br/><br/>"
        "<b>5. Testes.</b> Acessos autorizados OK; acessos indevidos negados; ACL leitura OK / escrita negada; "
        "sudo apenas para carlos/machado.<br/><br/>"
        "<b>6. Riscos remanescentes.</b> Revisar se machado deve permanecer admin em produção; "
        "fortalecer logging/auth; definir revisão periódica de ACL/sudo; avaliar sudoers por comando (não só ALL).<br/><br/>"
        "<b>7. Conclusão.</b> ☑ <b>O ambiente está apto, com ressalvas.</b><br/><br/>"
        "<b>8. Recomendações.</b> Revisão trimestral de identidades; sudo granular; MFA/SSH keys quando houver acesso remoto; "
        "monitoramento de auth.log/journal; inventário contínuo de ACL.",
        st["Body"]))

    story.append(Paragraph("Modelo de Registro das Alterações", st["H2"]))
    story.append(grid(
        ["Item", "Situação anterior", "Alteração", "Situação final", "Evidência"],
        [
            ["ana", "∈ sudo + infraestrutura", "gpasswd -d", "só desenvolvimento", "id ana"],
            ["temporario", "Ativa + sudo", "passwd -l + sair do sudo", "Bloqueada", "passwd -S"],
            ["backup", "∈ sudo", "gpasswd -d; nologin", "serviço mínimo", "getent passwd/group"],
            ["/financeiro", "inexistente/inadequado", "chown/chmod 770", "maria:financeiro 770", "ls -ld"],
            ["ACL paulo", "sem acesso", "setfacl -m / -x", "exceção removida", "getfacl"],
        ],
        st, [2.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.7*cm]
    ))

    story.append(Paragraph("Reflexão Final", st["H2"]))
    story.append(Paragraph(
        "<b>1.</b> Vulnerabilidade mais crítica: contas indevidas no grupo sudo (especialmente backup e temporario).<br/>"
        "<b>2.</b> Maior atenção técnica: ACL (concessão efetiva vs permissões de arquivo) e validação negativa de acessos.<br/>"
        "<b>3.</b> A maior contribuição vem da combinação; se for escolher um eixo, <b>usuários/grupos + menor privilégio no sudo</b> "
        "reduzem o impacto de qualquer falha de permissão pontual.<br/>"
        "<b>4.</b> Em empresas reais: joiner/mover/leaver, RBAC por grupos, ACL para exceções auditadas, "
        "sudo com accountability e revisões periódicas alinhadas a compliance.",
        st["Body"]))

    story.append(Spacer(1, 0.3*cm))
    story.append(hr())
    story.append(Paragraph(
        "Declaração: alterações realizadas em ambiente de laboratório (WSL/Debian), com registro de evidências. "
        "Nenhuma recomendação foi apresentada sem evidência correspondente.",
        st["Small"]))

    doc.build(story, onFirstPage=footer("Lab 02 — Identidades e Privilégios (Preenchido)"),
              onLaterPages=footer("Lab 02 — Identidades e Privilégios (Preenchido)"))
    print("LAB:", OUT_LAB)


if __name__ == "__main__":
    build_ordem_servico()
    build_lab_identidades()
    import shutil
    shutil.copy2(OUT_OS, DL_OS)
    shutil.copy2(OUT_LAB, DL_LAB)
    print("Downloads:", DL_OS)
    print("Downloads:", DL_LAB)
