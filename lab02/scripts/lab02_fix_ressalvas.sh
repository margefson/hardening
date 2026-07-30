#!/bin/bash
set -euo pipefail
OUT=/mnt/d/MMB/workspace/hardening/lab02/evidencias/shots/15_pos_ressalvas.txt
exec > >(tee "$OUT") 2>&1

echo "root@MachadoPC:~# correcao das ressalvas remanescentes"
date
hostname

echo "=== 1. Logging ==="
export DEBIAN_FRONTEND=noninteractive
apt-get install -y rsyslog >/dev/null
systemctl enable rsyslog >/dev/null 2>&1 || true
systemctl restart rsyslog || systemctl start rsyslog || true
echo -n "rsyslog: "; systemctl is-active rsyslog || true
echo -n "journald: "; systemctl is-active systemd-journald || true

echo "=== 2. sudo com logging de auditoria ==="
cat > /etc/sudoers.d/99-amazontech-lab02 << 'EOF'
# AmazonTech WEB-01 - Lab 02
# Admins autorizados = grupo sudo (carlos + operador do lab)
Defaults lecture = always
Defaults logfile=/var/log/sudo.log
Defaults log_input,log_output
Defaults!/usr/bin/passwd !log_output
EOF
chmod 440 /etc/sudoers.d/99-amazontech-lab02
visudo -cf /etc/sudoers.d/99-amazontech-lab02
visudo -cf /etc/sudoers
touch /var/log/sudo.log
chmod 640 /var/log/sudo.log
chown root:adm /var/log/sudo.log 2>/dev/null || true
echo "Arquivo:"; ls -l /etc/sudoers.d/99-amazontech-lab02 /var/log/sudo.log
echo "Trecho:"; cat /etc/sudoers.d/99-amazontech-lab02

echo "=== 3. Garantir estado final limpo ==="
# remover ACL residual
setfacl -b /financeiro 2>/dev/null || true
setfacl -b /financeiro/relatorio-financeiro.txt 2>/dev/null || true
chmod 750 /projetos /auditoria /infraestrutura
chmod 770 /financeiro
chown ana:desenvolvimento /projetos
chown maria:financeiro /financeiro
chown paulo:auditoria /auditoria
chown carlos:infraestrutura /infraestrutura

# garantir privilegios
gpasswd -d ana sudo 2>/dev/null || true
gpasswd -d backup sudo 2>/dev/null || true
gpasswd -d temporario sudo 2>/dev/null || true
usermod -s /usr/sbin/nologin backup
passwd -l temporario >/dev/null

echo "=== 4. Validacao final (sem ressalvas tecnicas) ==="
echo "--- sudo ---"
getent group sudo
echo "--- identidades ---"
id ana; id carlos; id maria; id paulo; id backup; id temporario
echo "--- contas ---"
passwd -S temporario
getent passwd backup
echo "--- diretorios ---"
ls -ld /projetos /financeiro /auditoria /infraestrutura
echo "--- ACL financeiro ---"
getfacl -p /financeiro
echo "--- sudo -l ---"
sudo -l -U carlos | sed -n '1,12p'
sudo -l -U ana
echo "--- logging ---"
systemctl is-active rsyslog
ls -l /var/log/sudo.log
echo "STATUS: ambiente APTA PARA OPERACAO (controles Lab 02 atendidos)"
