#!/bin/bash
# Lynis + resumo (set +e para aide/lynis exit codes)
set +e
OUT=/mnt/d/MMB/workspace/hardening/lab03/evidencias/lab03_evidence_part2.txt
{
echo ""
echo "===== MISSAO 7 LYNIS ====="
date
# restaurar hosts se necessario
sed -i '/Lab03-AIDE-SIM/d' /etc/hosts 2>/dev/null

lynis audit system 2>&1 | tee /tmp/lynis_out.log | tail -160

echo "--- report ---"
grep -E 'hardening_index|lynis_version' /var/log/lynis-report.dat 2>/dev/null | head -10
grep -i 'Hardening index' /tmp/lynis_out.log /var/log/lynis.log 2>/dev/null | head -10
grep '^suggestion\[' /var/log/lynis-report.dat 2>/dev/null | head -25
grep '^warning\[' /var/log/lynis-report.dat 2>/dev/null | head -15

echo "===== RESUMO FINAL ====="
echo "ssh: $(systemctl is-active ssh) / $(systemctl is-enabled ssh)"
ufw status | head -12
echo "fail2ban: $(systemctl is-active fail2ban)"
fail2ban-client status
echo "e2scrub_reap: $(systemctl is-enabled e2scrub_reap.service 2>&1)"
ls -lh /var/lib/aide/aide.db
grep hardening_index /var/log/lynis-report.dat 2>/dev/null
ss -tulpn | head -15
echo LAB03_PART2_DONE
} | tee -a "$OUT"

# append aide checks to evidence if not there
cat /tmp/aide_check1.log >> /mnt/d/MMB/workspace/hardening/lab03/evidencias/lab03_evidence.txt 2>/dev/null
echo '--- AIDE CHECK 2 ---' >> /mnt/d/MMB/workspace/hardening/lab03/evidencias/lab03_evidence.txt
cat /tmp/aide_check2.log >> /mnt/d/MMB/workspace/hardening/lab03/evidencias/lab03_evidence.txt 2>/dev/null
