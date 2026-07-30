#!/bin/bash
set -euo pipefail
OUT=/mnt/d/MMB/workspace/hardening/lab03/evidencias/lab03_evidence_part2.txt
export DEBIAN_FRONTEND=noninteractive
{
echo "===== MISSAO 6 AIDE ====="
date
aide --version | head -5

cat > /etc/aide/aide.conf.lab03 << 'EOF'
database_in=file:/var/lib/aide/aide.db
database_out=file:/var/lib/aide/aide.db.new
gzip_dbout=no
database_attrs = sha512
log_level=warning

NORMAL = p+i+n+u+g+s+b+m+c+sha512

/etc    NORMAL
/bin    NORMAL
/sbin   NORMAL
/usr/bin NORMAL
/usr/sbin NORMAL
!/var/lib/aide
!/etc/mtab
EOF

mkdir -p /var/lib/aide
rm -f /var/lib/aide/aide.db /var/lib/aide/aide.db.new

echo "--- init ---"
aide --config=/etc/aide/aide.conf.lab03 --init 2>&1 | tee /tmp/aide_init.log | tail -25
cp -a /var/lib/aide/aide.db.new /var/lib/aide/aide.db
ls -lh /var/lib/aide/aide.db

echo "--- check 1 ---"
aide --config=/etc/aide/aide.conf.lab03 --check 2>&1 | tee /tmp/aide_check1.log | tail -35

echo "Lab03-AIDE-SIM $(date)" >> /etc/hosts
echo "--- check 2 apos /etc/hosts ---"
aide --config=/etc/aide/aide.conf.lab03 --check 2>&1 | tee /tmp/aide_check2.log | tail -45
sed -i '/Lab03-AIDE-SIM/d' /etc/hosts || true

echo "===== MISSAO 7 LYNIS ====="
date
lynis audit system 2>&1 | tee /tmp/lynis_out.log | tail -150

echo "--- report ---"
grep -E 'hardening_index|lynis_version' /var/log/lynis-report.dat 2>/dev/null | head -10
grep -i 'Hardening index' /tmp/lynis_out.log /var/log/lynis.log 2>/dev/null | head -10
grep '^suggestion\[' /var/log/lynis-report.dat 2>/dev/null | head -25 || true
grep '^warning\[' /var/log/lynis-report.dat 2>/dev/null | head -15 || true

echo "===== RESUMO FINAL ====="
echo "ssh: $(systemctl is-active ssh) / $(systemctl is-enabled ssh)"
ufw status | head -12
echo "fail2ban: $(systemctl is-active fail2ban)"
fail2ban-client status
echo "e2scrub_reap: $(systemctl is-enabled e2scrub_reap.service 2>&1)"
ls -lh /var/lib/aide/aide.db
grep hardening_index /var/log/lynis-report.dat 2>/dev/null || true
ss -tulpn | head -15
echo LAB03_PART2_DONE
} | tee "$OUT"
