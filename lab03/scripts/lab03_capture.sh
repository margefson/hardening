#!/bin/bash
OUT=/mnt/d/MMB/workspace/hardening/lab03/evidencias/shots
mkdir -p "$OUT"

snap() {
  local n="$1"; shift
  { echo "root@MachadoPC:~# $*"; eval "$@" 2>&1; echo; } > "$OUT/${n}.txt"
  echo saved "$n"
}

snap 01_inventario_servicos "systemctl list-units --type=service --state=running --no-pager; echo '--- enabled ---'; systemctl list-unit-files --type=service --state=enabled --no-pager"
snap 02_portas "ss -tulpn; echo '--- hostname ---'; hostnamectl | head -12"
snap 03_menor_func "echo 'e2scrub_reap:'; systemctl is-enabled e2scrub_reap.service; systemctl is-active e2scrub_reap.service; echo 'exim4:'; systemctl is-enabled exim4 2>&1; systemctl is-active exim4 2>&1"
snap 04_ssh_status "systemctl status ssh --no-pager | head -22; echo '--- params ---'; grep -E '^(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication|X11Forwarding|MaxAuthTries|AllowUsers)' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null; echo '--- sshd -t ---'; sshd -t && echo 'sshd_config OK'"
snap 05_ufw "ufw status verbose; echo '--- numbered ---'; ufw status numbered"
snap 06_fail2ban "systemctl status fail2ban --no-pager | head -18; echo '--- client ---'; fail2ban-client status; fail2ban-client status sshd"
snap 07_aide "aide --version | head -3; ls -lh /var/lib/aide/aide.db; echo '--- check1 (OK) ---'; tail -20 /tmp/aide_check1.log; echo '--- check2 (detectou /etc/hosts) ---'; tail -35 /tmp/aide_check2.log"
snap 08_lynis "grep -E 'hardening_index|lynis_version' /var/log/lynis-report.dat; echo '--- Hardening index ---'; grep -i 'Hardening index' /var/log/lynis.log | tail -3; echo '--- top suggestions ---'; grep '^suggestion\[' /var/log/lynis-report.dat | head -15; echo '--- warnings ---'; grep '^warning\[' /var/log/lynis-report.dat | head -10"

# consolidar evidencia
cat /mnt/d/MMB/workspace/hardening/lab03/evidencias/lab03_evidence.txt /mnt/d/MMB/workspace/hardening/lab03/evidencias/lab03_evidence_part2.txt /tmp/lynis_out.log 2>/dev/null | tail -5 >/dev/null
echo CAPTURE_DONE
