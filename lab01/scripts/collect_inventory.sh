#!/bin/bash
set -euo pipefail

OUT="/mnt/d/MMB/workspace/hardening/lab01/evidencias/inventory_raw.txt"
exec >"$OUT" 2>&1

echo "=== ETAPA 1: SISTEMA ==="
echo "--- os-release ---"
cat /etc/os-release
echo "--- kernel ---"
uname -a
echo "--- hostname ---"
hostname
hostnamectl 2>/dev/null || true
echo "--- date ---"
date
timedatectl 2>/dev/null || true
echo "--- uptime ---"
uptime

echo ""
echo "=== ETAPA 2: USUARIOS E GRUPOS ==="
echo "--- /etc/passwd ---"
getent passwd
echo "--- grupos ---"
getent group
echo "--- grupo sudo ---"
getent group sudo 2>/dev/null || true
echo "--- grupo adm ---"
getent group adm 2>/dev/null || true
echo "--- UID 0 ---"
awk -F: '$3==0{print}' /etc/passwd
echo "--- usuarios com shell de login ---"
awk -F: '$7 !~ /(nologin|false)/ {print $1":"$3":"$7}' /etc/passwd
echo "--- last ---"
last -n 20 2>/dev/null || true
echo "--- who ---"
who 2>/dev/null || true

echo ""
echo "=== ETAPA 3: SERVICOS ==="
echo "--- systemctl running ---"
systemctl list-units --type=service --state=running --no-pager 2>/dev/null || true
echo "--- systemctl enabled ---"
systemctl list-unit-files --type=service --state=enabled --no-pager 2>/dev/null || true
echo "--- ps ---"
ps aux --sort=-%mem | head -40

echo ""
echo "=== ETAPA 4: REDE ==="
echo "--- interfaces ---"
ip -br addr 2>/dev/null || ifconfig -a 2>/dev/null || true
echo "--- ip route ---"
ip route 2>/dev/null || true
echo "--- ss listening ---"
ss -tulnp 2>/dev/null || netstat -tulnp 2>/dev/null || true
echo "--- firewall ufw ---"
ufw status verbose 2>/dev/null || true
echo "--- iptables ---"
iptables -L -n -v 2>/dev/null || true
echo "--- nft ---"
nft list ruleset 2>/dev/null || true

echo ""
echo "=== ETAPA 5: ATUALIZACOES E LOGS ==="
echo "--- apt update (check only) ---"
apt-get update -qq 2>&1 | tail -20 || true
echo "--- upgrades pending ---"
apt list --upgradable 2>/dev/null | head -50 || true
echo "--- unattended-upgrades ---"
dpkg -l | grep -E 'unattended|apt-listchanges' || true
echo "--- log files ---"
ls -lah /var/log 2>/dev/null | head -60
echo "--- journald ---"
journalctl --disk-usage 2>/dev/null || true
echo "--- recent journal errors ---"
journalctl -p err -n 30 --no-pager 2>/dev/null || true
echo "--- auth log tail ---"
tail -n 30 /var/log/auth.log 2>/dev/null || tail -n 30 /var/log/secure 2>/dev/null || journalctl -u ssh -n 20 --no-pager 2>/dev/null || true
echo "--- syslog mechanism ---"
systemctl is-active rsyslog 2>/dev/null || true
systemctl is-active systemd-journald 2>/dev/null || true
ls /etc/rsyslog.conf 2>/dev/null || true
ls /etc/systemd/journald.conf 2>/dev/null || true

echo ""
echo "=== COLETA CONCLUIDA ==="
date
