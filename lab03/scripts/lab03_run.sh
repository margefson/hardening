#!/bin/bash
# Lab 03 - Reducao da Superficie de Ataque
set -euo pipefail
OUTDIR=/mnt/d/MMB/workspace/hardening/lab03/evidencias/shots
mkdir -p "$OUTDIR"
EV=/mnt/d/MMB/workspace/hardening/lab03/evidencias/lab03_evidence.txt
export DEBIAN_FRONTEND=noninteractive

log() { echo; echo "===== $* ====="; date '+%Y-%m-%d %H:%M:%S'; }

{
log "INICIO LAB 03 - $(hostname) - $(whoami)"

log "MISSAO 1 - INVENTARIO INICIAL"
echo "--- hostname/kernel ---"
hostnamectl 2>/dev/null | head -15 || true
uname -a
echo "--- servicos running ---"
systemctl list-units --type=service --state=running --no-pager
echo "--- enabled ---"
systemctl list-unit-files --type=service --state=enabled --no-pager
echo "--- ss ---"
ss -tulpn 2>/dev/null || ss -tuln
echo "--- ps (top) ---"
ps aux --sort=-%mem | head -25

log "MISSAO 2 - MENOR FUNCIONALIDADE"
# Candidato: e2scrub_reap (manutencao ext4, nao essencial em WSL lab)
echo "--- situacao inicial e2scrub_reap ---"
systemctl status e2scrub_reap.service --no-pager 2>&1 | head -15 || true
systemctl is-enabled e2scrub_reap.service 2>&1 || true
systemctl stop e2scrub_reap.service 2>/dev/null || true
systemctl disable e2scrub_reap.service 2>/dev/null || true
echo "--- apos disable ---"
systemctl is-enabled e2scrub_reap.service 2>&1 || true
systemctl is-active e2scrub_reap.service 2>&1 || true
# getty permanece (console)

log "MISSAO 3 - SSH HARDENING"
apt-get install -y openssh-server >/tmp/lab03_ssh_install.log 2>&1 || true
# garantir diretorio run
mkdir -p /run/sshd
# backup config
cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.lab03 2>/dev/null || true
# drop-in hardening
mkdir -p /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/99-amazontech-hardening.conf << 'EOF'
# AmazonTech WEB-01 - Lab 03 SSH Hardening
PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
LoginGraceTime 30
AllowUsers machado carlos
Protocol 2
EOF
# Em algumas distros PasswordAuthentication fica no config principal - sobrescrever
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^#\?X11Forwarding.*/X11Forwarding no/' /etc/ssh/sshd_config
sshd -t
systemctl enable ssh 2>/dev/null || systemctl enable sshd 2>/dev/null || true
systemctl restart ssh 2>/dev/null || systemctl restart sshd 2>/dev/null || true
echo "--- status ssh ---"
systemctl status ssh --no-pager 2>&1 | head -20 || systemctl status sshd --no-pager 2>&1 | head -20 || true
echo "--- params ---"
grep -E '^(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication|X11Forwarding|Port|MaxAuthTries|AllowUsers)' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null || true
echo "--- porta ---"
ss -tulpn | grep -E 'ssh|:22' || true

log "MISSAO 4 - UFW FIREWALL"
apt-get install -y ufw >/tmp/lab03_ufw_install.log 2>&1 || true
echo "--- ufw antes ---"
ufw status verbose 2>&1 || true
# politica: default deny incoming, allow SSH
ufw --force reset >/dev/null 2>&1 || true
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH || ufw allow 22/tcp
# HTTP nao necessario neste lab (sem app web) - nao liberar 80
ufw --force enable
echo "--- ufw depois ---"
ufw status verbose
ufw status numbered
echo "--- ss apos ufw ---"
ss -tuln

log "MISSAO 5 - FAIL2BAN"
apt-get install -y fail2ban >/tmp/lab03_f2b_install.log 2>&1 || true
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime  = 10m
findtime = 10m
maxretry = 3
backend  = systemd

[sshd]
enabled = true
port    = ssh
filter  = sshd
maxretry = 3
EOF
systemctl enable fail2ban
systemctl restart fail2ban || true
sleep 2
echo "--- status fail2ban ---"
systemctl status fail2ban --no-pager 2>&1 | head -20 || true
fail2ban-client status 2>&1 || true
fail2ban-client status sshd 2>&1 || true
journalctl -u fail2ban -n 20 --no-pager 2>&1 || true

log "MISSAO 6 - AIDE"
apt-get install -y aide aide-common >/tmp/lab03_aide_install.log 2>&1 || true
# init baseline (pode demorar)
echo "--- aide versao ---"
aide --version 2>&1 | head -3 || true
ls -la /etc/aide/aide.conf 2>/dev/null || ls -la /etc/aide.conf 2>/dev/null || true
# Debian usa aideinit
if command -v aideinit >/dev/null; then
  aideinit -y -f 2>&1 | tail -30 || true
  if [ -f /var/lib/aide/aide.db.new ]; then
    cp -a /var/lib/aide/aide.db.new /var/lib/aide/aide.db
  fi
elif aide --init 2>&1 | tee /tmp/aide_init.log | tail -20; then
  DBNEW=$(ls /var/lib/aide/aide.db.new* 2>/dev/null | head -1 || true)
  if [ -n "${DBNEW:-}" ]; then cp -a "$DBNEW" /var/lib/aide/aide.db; fi
fi
echo "--- aide check 1 ---"
aide --check 2>&1 | tee /tmp/aide_check1.log | tail -40 || aide.wrapper --check 2>&1 | tee /tmp/aide_check1.log | tail -40 || true
# simulacao controlada
echo "Lab03 AIDE test $(date)" >> /etc/hosts
echo "--- aide check 2 (apos alteracao /etc/hosts) ---"
aide --check 2>&1 | tee /tmp/aide_check2.log | tail -50 || aide.wrapper --check 2>&1 | tee /tmp/aide_check2.log | tail -50 || true
# restaurar hosts e atualizar baseline opcionalmente
# (manter alteracao detectada como evidencia; reverter hosts)
sed -i '/Lab03 AIDE test/d' /etc/hosts || true

log "MISSAO 7 - LYNIS"
apt-get install -y lynis >/tmp/lab03_lynis_install.log 2>&1 || true
lynis audit system --quick 2>&1 | tee /tmp/lynis_out.log | tail -80 || true
echo "--- hardening index ---"
grep -E 'Hardening index|hardening_index|warnings|suggestions' /var/log/lynis.log /var/log/lynis-report.dat 2>/dev/null | head -40 || true
grep suggestion /var/log/lynis-report.dat 2>/dev/null | head -25 || true

log "AUDITORIA FINAL RESUMO"
echo "ssh:"; systemctl is-active ssh 2>/dev/null || systemctl is-active sshd 2>/dev/null || true
echo "ufw:"; ufw status | head -15
echo "fail2ban:"; systemctl is-active fail2ban; fail2ban-client status 2>&1 | head -10
echo "aide db:"; ls -la /var/lib/aide/aide.db 2>/dev/null || ls -la /var/lib/aide/ 2>/dev/null | head -10
echo "lynis:"; grep -E 'hardening_index|lynis_version' /var/log/lynis-report.dat 2>/dev/null | head -10
ss -tulpn | head -20
systemctl list-units --type=service --state=running --no-pager | head -25

log "FIM LAB 03"
} | tee "$EV"

# extrair shots textuais principais
cp -f "$EV" "$OUTDIR/00_full.txt" 2>/dev/null || true
echo LAB03_DONE
