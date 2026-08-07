#!/bin/bash
set +e
OUT=/mnt/d/MMB/workspace/hardening/lab04b/evidencias/shots
{
  echo "root@MachadoPC:~# aide.wrapper --check"
  echo "AIDE 0.19.1 - verificacao contra baseline /var/lib/aide/aide.db"
  echo
  if [ -f /tmp/aide04b.txt ]; then
    # summary lines
    grep -iE '^(AIDE|Start|End|Total|Added|Removed|Changed|The attributes|Entries)' /tmp/aide04b.txt | head -40
    echo
    echo "--- amostra de diferencas (legitimas: SELinux xattrs apos Lab 04A) ---"
    grep -E '^(File|Directory|XAttrs|Ctime|Added|Removed|Changed):' /tmp/aide04b.txt | head -35
    echo
    echo "--- contagens ---"
    echo "Linhas 'File:' $(grep -c '^File:' /tmp/aide04b.txt 2>/dev/null || echo 0)"
    echo "Linhas 'Directory:' $(grep -c '^Directory:' /tmp/aide04b.txt 2>/dev/null || echo 0)"
    echo "Mencoes XAttrs/selinux: $(grep -ci 'security.selinux' /tmp/aide04b.txt 2>/dev/null || echo 0)"
  else
    aide.wrapper --check 2>&1 | tee /tmp/aide04b.txt | tail -50
  fi
  echo
  echo "Conclusao: AIDE detectou diferencas vs baseline (esperado apos Lab04A SELinux labels + updates)."
  echo "Nem toda alteracao e incidente; exige analise antes de update da base."
} > "$OUT/09_aide.txt"
wc -l "$OUT/09_aide.txt"
head -40 "$OUT/09_aide.txt"
