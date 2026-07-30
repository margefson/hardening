#!/bin/bash
OUT=/mnt/d/MMB/workspace/hardening/lab01/evidencias/shots
mkdir -p "$OUT"

run() {
  local name="$1"; shift
  {
    echo "root@MachadoPC:~# $*"
    eval "$@" 2>&1
    echo
  } > "$OUT/${name}.txt"
  echo "saved $name"
}

run 01_sistema "cat /etc/os-release; echo '---'; uname -a; echo '---'; hostnamectl; echo '---'; date; timedatectl | head -8"
run 02_usuarios "getent passwd | awk -F: '\$3==0 || \$3>=1000 || \$1~/^(backup|www-data|daemon)$/ {print}'; echo '--- login shells ---'; awk -F: '\$7 !~ /(nologin|false)/ {print}' /etc/passwd"
run 03_grupos "getent group sudo; getent group adm; getent group | egrep 'desenvolvimento|infraestrutura|financeiro|auditoria|sudo' || true"
run 04_servicos "systemctl list-units --type=service --state=running --no-pager; echo '--- enabled ---'; systemctl list-unit-files --type=service --state=enabled --no-pager"
run 05_rede "ip -br addr; echo '--- route ---'; ip route; echo '--- listening ---'; ss -tulnp"
run 06_firewall "command -v ufw; ufw status 2>&1 || true; echo '--- iptables (filter) ---'; iptables -L -n 2>&1 | head -30 || true"
run 07_atualizacoes "apt list --upgradable 2>/dev/null; echo 'count upgradable:'; apt list --upgradable 2>/dev/null | grep -c upgradable || true; echo '--- debian_version ---'; cat /etc/debian_version; dpkg -l sudo systemd libc6 openssl | grep ^ii"
run 08_logs "ls -lah /var/log | head -25; echo '--- journal ---'; journalctl --disk-usage; echo '--- rsyslog/journald ---'; systemctl is-active rsyslog; systemctl is-active systemd-journald; echo '--- login.defs pass ---'; grep -E '^PASS_' /etc/login.defs"

echo DONE
