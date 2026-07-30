#!/bin/bash
# AIDE completo (Debian) excluindo mounts WSL/Windows que causam travamento
set +e
OUT=/mnt/d/MMB/workspace/hardening/lab03/evidencias/shots
EV=/mnt/d/MMB/workspace/hardening/lab03/evidencias/lab03_aide_full.txt
mkdir -p "$OUT" /var/log/aide /var/lib/aide

{
echo "root@MachadoPC:~# AIDE full init com exclusoes WSL"
date
hostname

# Exclusoes antes da regra catch-all 99_aide_root
# Sintaxe AIDE 0.19: -/path$ 0  = ignore recursivo
cat > /etc/aide/aide.conf.d/98_wsl_exclusions << 'EOF'
# Exclusoes WSL/Windows - evita scan de /mnt/c /mnt/d /mnt/f (centenas de GB)
-/mnt$ 0
-/usr/lib/wsl$ 0
-/usr/lib/modules$ 0
-/init$ 0
EOF

echo "--- exclusoes ---"
cat /etc/aide/aide.conf.d/98_wsl_exclusions

echo "--- validar config ---"
aide --config=/etc/aide/aide.conf --config-check 2>&1 | tail -20

echo "--- removendo DB anterior ---"
rm -f /var/lib/aide/aide.db /var/lib/aide/aide.db.new

echo "--- aideinit (baseline completa Debian, sem /mnt) ---"
# -y assume yes, -f force
TIMEFORMAT='real %R s'
time aideinit -y -f 2>&1 | tee /tmp/aide_full_init.log | tail -40
INIT_RC=${PIPESTATUS[0]}
echo "aideinit exit=$INIT_RC"

if [ -f /var/lib/aide/aide.db.new ]; then
  cp -a /var/lib/aide/aide.db.new /var/lib/aide/aide.db
fi
ls -lh /var/lib/aide/aide.db* 2>/dev/null

echo "--- entries no log ---"
grep -E 'Number of entries|successfully|ERROR|End timestamp|Start timestamp' /tmp/aide_full_init.log | tail -20

echo "--- check 1 ---"
aide --check 2>&1 | tee /tmp/aide_full_check1.log | tail -35
echo "check1 exit=$?"

echo "Lab03-AIDE-FULL-SIM $(date)" >> /etc/hosts
echo "--- check 2 apos alteracao /etc/hosts ---"
aide --check 2>&1 | tee /tmp/aide_full_check2.log | tail -45
echo "check2 exit=$?"
sed -i '/Lab03-AIDE-FULL-SIM/d' /etc/hosts

echo "--- resumo ---"
ls -lh /var/lib/aide/aide.db
grep -E 'Number of entries|NO differences|Changed entries|Added entries' /tmp/aide_full_check1.log /tmp/aide_full_check2.log | head -30
echo AIDE_FULL_DONE
} | tee "$EV"

# snapshot para PDF
{
  echo "root@MachadoPC:~# aideinit -y -f  # com exclusao /mnt (WSL)"
  grep -E 'Start timestamp|successfully|Number of entries|End timestamp|ERROR|SHA512|New AIDE' /tmp/aide_full_init.log | head -30
  echo
  echo "root@MachadoPC:~# ls -lh /var/lib/aide/aide.db; aide --check"
  ls -lh /var/lib/aide/aide.db
  grep -E 'NO differences|differences|Number of entries|Changed entries|Added|/etc/hosts|Summary' /tmp/aide_full_check1.log /tmp/aide_full_check2.log | head -40
} > "$OUT/07_aide.txt"

echo CAPTURE_UPDATED
