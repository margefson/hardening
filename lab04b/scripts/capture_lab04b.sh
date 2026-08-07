#!/bin/bash
set +e
export DEBIAN_FRONTEND=noninteractive
OUT=/mnt/d/MMB/workspace/hardening/lab04b/evidencias
SHOT="$OUT/shots"
RAW="$OUT/raw"
mkdir -p "$SHOT" "$RAW"

# DNS fallback
if ! getent hosts deb.debian.org >/dev/null 2>&1; then
  echo "nameserver 8.8.8.8" > /etc/resolv.conf
  echo "nameserver 1.1.1.1" >> /etc/resolv.conf
fi

echo "=== INSTALL TOOLS ==="
apt-get update -qq
apt-get install -y debsecan debsums 2>&1 | tail -20
# lynis/aide likely already installed from lab03
command -v lynis || apt-get install -y lynis 2>&1 | tail -10
command -v aide || apt-get install -y aide 2>&1 | tail -10

{
  echo "root@MachadoPC:~# hostname; date"
  hostname; date
  echo "root@MachadoPC:~# cat /etc/os-release | head -8"
  cat /etc/os-release | head -8
  echo "root@MachadoPC:~# uname -a"
  uname -a
} > "$SHOT/01_ambiente.txt"

{
  echo "root@MachadoPC:~# apt-get update"
  apt-get update 2>&1
} > "$SHOT/02_apt_update.txt"

{
  echo "root@MachadoPC:~# apt list --upgradable 2>/dev/null"
  apt list --upgradable 2>/dev/null
  echo
  echo "Total upgradable (excl header):" $(apt list --upgradable 2>/dev/null | grep -vc '^Listing')
} > "$SHOT/03_apt_upgradable.txt"

{
  echo "root@MachadoPC:~# apt-get -s upgrade 2>&1 | head -60"
  apt-get -s upgrade 2>&1 | head -60
  echo
  echo "root@MachadoPC:~# # Decisao: aplicar atualizacoes de seguranca no lab"
  echo "root@MachadoPC:~# apt-get -y upgrade 2>&1 | tail -40"
  apt-get -y upgrade 2>&1 | tee /tmp/lab04b_upgrade.log | tail -40
  echo
  echo "--- resumo ---"
  grep -E 'upgraded|newly installed|to remove|not upgraded' /tmp/lab04b_upgrade.log | tail -5
} > "$SHOT/04_apt_upgrade.txt"

{
  echo "root@MachadoPC:~# # Equivalente Debian a ubuntu-security-status"
  echo "root@MachadoPC:~# dpkg -l | grep -c '^ii'"
  echo "Pacotes instalados (ii):" $(dpkg -l | grep -c '^ii')
  echo
  echo "root@MachadoPC:~# apt-get -s upgrade 2>&1 | grep -iE 'security|upgraded|kept' | head -20"
  apt-get -s dist-upgrade 2>&1 | head -25
  echo
  if command -v ubuntu-security-status >/dev/null 2>&1; then
    echo "root@MachadoPC:~# ubuntu-security-status"
    ubuntu-security-status 2>&1 | head -40
  else
    echo "# ubuntu-security-status: nao disponivel no Debian"
    echo "# Equivalente: contagem de pacotes + repositorios security + debsecan"
    echo "root@MachadoPC:~# grep -r security /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null | head -15"
    grep -r security /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null | head -15
    echo
    echo "root@MachadoPC:~# apt-cache policy | head -20"
    apt-cache policy 2>&1 | head -20
  fi
} > "$SHOT/05_security_status.txt"

{
  echo "root@MachadoPC:~# debsecan --suite trixie 2>&1 | head -50"
  # debsecan may need suite; try default then trixie
  debsecan 2>&1 | head -50
  echo
  echo "--- contagem CVE unicos (amostra) ---"
  debsecan 2>/dev/null | grep -oE 'CVE-[0-9]+-[0-9]+' | sort -u | wc -l
  echo "CVEs unicos (total linhas CVE):" $(debsecan 2>/dev/null | grep -c 'CVE-' || echo 0)
  echo
  echo "--- top pacotes citados ---"
  debsecan 2>/dev/null | awk '/^[a-z0-9].*CVE/ {print $1}' | sort | uniq -c | sort -rn | head -15
  # alternate parse
  debsecan 2>/dev/null | grep CVE | sed 's/.* //' | head -5
  echo
  echo "root@MachadoPC:~# debsecan 2>&1 | grep -iE 'openssl|openssh|linux-image|sudo|libc6' | head -20"
  debsecan 2>&1 | grep -iE 'openssl|openssh|linux-image|sudo|libc6|bash' | head -20
} > "$SHOT/06_debsecan.txt"

{
  echo "root@MachadoPC:~# # dnf updateinfo: N/A no Debian (Rocky/RHEL)"
  echo "# Equivalente interpretativo: apt-get changelog / security pocket"
  echo "root@MachadoPC:~# apt-get -s upgrade 2>&1 | grep -i security | head -15 || true"
  apt-cache search '^linux-image' 2>/dev/null | head -5
  echo
  echo "# Conclusao: em Rocky usariamos 'dnf updateinfo list security'."
  echo "# No Debian/Ubuntu priorizamos security.debian.org + debsecan + apt upgrade."
} > "$SHOT/07_dnf_updateinfo_na.txt"

{
  echo "root@MachadoPC:~# lynis audit system --quick 2>&1 | tee /tmp/lynis04b.txt | tail -80"
  # full audit may take time; use normal audit
  lynis audit system 2>&1 | tee /tmp/lynis04b_full.txt | tail -100
  echo
  echo "=== EXTRACT ==="
  grep -iE 'hardening index|warnings|suggestions|lynis.*done' /tmp/lynis04b_full.txt | tail -20
  # also from report
  RPT=$(ls -1t /var/log/lynis-report.dat 2>/dev/null | head -1)
  if [ -n "$RPT" ]; then
    echo "Report: $RPT"
    grep -E 'hardening_index|warning\[|suggestion\[' "$RPT" | head -40
    echo "warnings count:" $(grep -c 'warning\[' "$RPT" 2>/dev/null)
    echo "suggestions count:" $(grep -c 'suggestion\[' "$RPT" 2>/dev/null)
    grep 'hardening_index=' "$RPT"
  fi
} > "$SHOT/08_lynis.txt"

{
  echo "root@MachadoPC:~# aide --version 2>&1 | head -3"
  aide --version 2>&1 | head -3
  echo
  echo "root@MachadoPC:~# aide --check 2>&1 | tee /tmp/aide04b.txt | tail -60"
  # aide check can be slow; try aide.wrapper or aide -c
  if [ -x /usr/bin/aide.wrapper ]; then
    aide.wrapper --check 2>&1 | tee /tmp/aide04b.txt | tail -80
  else
    aide --check 2>&1 | tee /tmp/aide04b.txt | tail -80
  fi
  echo
  echo "=== SUMMARY ==="
  grep -iE 'AIDE|entries|added|removed|changed|differences|OK|Looks' /tmp/aide04b.txt | head -40
} > "$SHOT/09_aide.txt"

{
  echo "root@MachadoPC:~# debsums -c 2>&1 | tee /tmp/debsums04b.txt | head -40"
  # -c only report changed; full debsums is huge
  debsums -c 2>&1 | tee /tmp/debsums04b.txt | head -50
  EC=$?
  echo
  echo "exit_code=$EC (0=sem inconsistencias reportadas por -c)"
  echo "linhas alteradas:" $(wc -l < /tmp/debsums04b.txt)
  if [ ! -s /tmp/debsums04b.txt ]; then
    echo "Nenhuma inconsistencia reportada por debsums -c (checksums OK ou silencio)."
  fi
  echo
  echo "root@MachadoPC:~# debsums --help | head -15"
  debsums --help 2>&1 | head -15
} > "$SHOT/10_debsums.txt"

# compact lynis for shot if too long - keep file as is for PDF truncate

cat "$SHOT"/0*.txt > "$RAW/lab04b_full.txt" 2>/dev/null
ls -la "$SHOT"
echo "CAPTURE DONE"
