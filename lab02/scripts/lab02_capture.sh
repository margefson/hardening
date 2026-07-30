#!/bin/bash
# Captura evidencias reais do Lab 02 em arquivos de texto
OUTDIR=/mnt/d/MMB/workspace/hardening/lab02/evidencias/shots
mkdir -p "$OUTDIR"
cd "$OUTDIR"

run() {
  local name="$1"; shift
  {
    echo "root@MachadoPC:~# $*"
    eval "$@" 2>&1
    echo
  } > "${name}.txt"
  echo "saved $name"
}

run 01_hostname_date "hostname; date; cat /etc/debian_version; uname -r"
run 02_usuarios "getent passwd ana carlos maria paulo backup temporario machado root"
run 03_id_usuarios "id ana; id carlos; id maria; id paulo; id backup; id temporario"
run 04_grupos "getent group desenvolvimento infraestrutura financeiro auditoria sudo"
run 05_sudo_final "getent group sudo; echo '---'; passwd -S temporario; getent passwd backup"
run 06_diretorios "ls -ld /projetos /financeiro /auditoria /infraestrutura"
run 07_arquivos "ls -l /projetos /financeiro /auditoria /infraestrutura"
run 08_acesso_ok "sudo -u ana ls /projetos; sudo -u maria ls /financeiro; sudo -u paulo ls /auditoria; sudo -u carlos ls /infraestrutura"
run 09_acesso_negado "sudo -u ana ls /financeiro; sudo -u maria ls /infraestrutura; sudo -u paulo ls /projetos"
run 10_acl_demo "setfacl -m u:paulo:rx /financeiro; setfacl -m u:paulo:r /financeiro/relatorio-financeiro.txt; echo '=== getfacl ==='; getfacl /financeiro; echo '=== ls -ld ==='; ls -ld /financeiro; echo '=== paulo ls ==='; sudo -u paulo ls /financeiro; echo '=== paulo touch (deve falhar) ==='; sudo -u paulo touch /financeiro/teste-auditoria.txt; echo '=== id paulo ==='; id paulo"
run 11_acl_remove "setfacl -x u:paulo /financeiro; setfacl -x u:paulo /financeiro/relatorio-financeiro.txt; setfacl -b /financeiro 2>/dev/null; echo '=== getfacl apos remocao ==='; getfacl /financeiro; echo '=== paulo ls (deve falhar) ==='; sudo -u paulo ls /financeiro; ls -ld /financeiro"
run 12_sudo_l "sudo -l -U carlos; echo '===='; sudo -l -U ana; echo '===='; sudo -l -U maria; echo '===='; sudo -l -U paulo"
run 13_sudoers "grep -E '^%sudo|^root|^Defaults' /etc/sudoers; systemctl is-active cron"
run 14_auditoria_final "echo '=== SUDO ==='; getent group sudo; echo '=== IDS ==='; id ana; id carlos; id maria; id paulo; id backup; id temporario; echo '=== DIRS ==='; ls -ld /projetos /financeiro /auditoria /infraestrutura; echo '=== TEMPORARIO ==='; passwd -S temporario"

echo DONE
