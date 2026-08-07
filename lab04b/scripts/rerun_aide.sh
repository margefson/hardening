#!/bin/bash
set +e
OUT=/mnt/d/MMB/workspace/hardening/lab04b/evidencias/shots
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

echo "Running AIDE check (may take ~2min)..."
if [ -x /usr/bin/aide.wrapper ]; then
  /usr/bin/aide.wrapper --check > /tmp/aide04b.txt 2>&1
elif [ -x /usr/sbin/aide ]; then
  /usr/sbin/aide -c /etc/aide/aide.conf --check > /tmp/aide04b.txt 2>&1
else
  aide -c /etc/aide/aide.conf --check > /tmp/aide04b.txt 2>&1
fi
EC=$?
echo "aide exit=$EC lines=$(wc -l < /tmp/aide04b.txt)"

{
  echo "root@MachadoPC:~# aide.wrapper --check"
  echo "AIDE 0.19.1 | baseline: /var/lib/aide/aide.db | exit=$EC"
  echo
  grep -iE '^(AIDE|Start timestamp|End timestamp|Total number|Added|Removed|Changed|The attributes|Entries processed)' /tmp/aide04b.txt | head -30
  echo
  # AIDE 0.19 format may differ
  head -40 /tmp/aide04b.txt
  echo
  echo "... (detalhes truncados) ..."
  echo
  echo "File entries mentioned: $(grep -cE '^(File|Directory):' /tmp/aide04b.txt)"
  echo "security.selinux xattr diffs: $(grep -ci 'security.selinux' /tmp/aide04b.txt)"
  echo
  echo "Amostra de alteracoes:"
  grep -E '^(File|Directory):' /tmp/aide04b.txt | head -15
  echo
  echo "Conclusao: diferencas vs baseline - esperado (Lab04A SELinux labels + apt upgrade libexpat1)."
  echo "Nao trataremos automaticamente como incidente; analisar e atualizar DB apos janela."
} > "$OUT/09_aide.txt"

wc -l "$OUT/09_aide.txt"
head -45 "$OUT/09_aide.txt"
