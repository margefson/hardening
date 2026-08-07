#!/bin/bash
set +e
OUT=/mnt/d/MMB/workspace/hardening/lab04a/evidencias/shots
mkdir -p "$OUT"

{
  echo "root@MachadoPC:~# cat /etc/os-release | head -8"
  cat /etc/os-release | head -8
  echo "root@MachadoPC:~# uname -a"
  uname -a
  echo "root@MachadoPC:~# hostname; date"
  hostname; date
} > "$OUT/01_ambiente.txt"

{
  echo "root@MachadoPC:~# for c in sestatus getenforce restorecon semanage; do command -v \$c || echo \$c: NAO INSTALADO; done"
  for c in sestatus getenforce restorecon semanage; do
    command -v "$c" || echo "$c: NAO INSTALADO"
  done
  echo "root@MachadoPC:~# sestatus"
  sestatus 2>&1 || true
  echo "root@MachadoPC:~# getenforce"
  getenforce 2>&1 || true
  echo "root@MachadoPC:~# dpkg -l | grep -i selinux | head -8"
  dpkg -l | grep -i selinux | head -8
} > "$OUT/02_selinux_ausente.txt"

{
  echo "root@MachadoPC:~# ls -lZ / | head -20"
  ls -lZ / 2>&1 | head -20
  echo
  echo "root@MachadoPC:~# ls -lZ /etc | head -12"
  ls -lZ /etc 2>&1 | head -12
  echo
  echo "# Observacao: contexto SELinux = ? (sem labels; Debian/WSL sem SELinux)"
} > "$OUT/03_ls_Z.txt"

{
  echo "root@MachadoPC:~# ps -eZ | head -20"
  ps -eZ 2>&1 | head -20
  echo
  echo "# Observacao: LABEL=kernel (WSL). Sem dominios SELinux (httpd_t etc.)"
} > "$OUT/04_ps_Z.txt"

{
  echo "root@MachadoPC:~# dpkg -l | grep -i apparmor"
  dpkg -l | grep -i apparmor
  echo
  echo "root@MachadoPC:~# ls /etc/apparmor.d | wc -l"
  echo "Arquivos em /etc/apparmor.d: $(ls /etc/apparmor.d | wc -l)"
  echo "root@MachadoPC:~# ls /etc/apparmor.d | head -25"
  ls /etc/apparmor.d | head -25
} > "$OUT/05_apparmor_pacotes.txt"

{
  echo "root@MachadoPC:~# systemctl status apparmor --no-pager | head -18"
  systemctl status apparmor --no-pager 2>&1 | head -18
  echo
  echo "root@MachadoPC:~# aa-status"
  aa-status 2>&1
  echo
  echo "root@MachadoPC:~# cat /sys/kernel/security/lsm"
  cat /sys/kernel/security/lsm 2>&1 || echo "LSM path indisponivel (WSL2)"
} > "$OUT/06_aa_status.txt"

{
  echo "root@MachadoPC:~# head -25 /etc/apparmor.d/bin.ping"
  head -25 /etc/apparmor.d/bin.ping 2>&1
  echo
  echo "root@MachadoPC:~# aa-enforce --help | head -8"
  aa-enforce --help 2>&1 | head -8
  echo "root@MachadoPC:~# aa-complain --help | head -8"
  aa-complain --help 2>&1 | head -8
  echo "root@MachadoPC:~# aa-logprof --help | head -10"
  aa-logprof --help 2>&1 | head -10
  echo "root@MachadoPC:~# aa-genprof --help | head -10"
  aa-genprof --help 2>&1 | head -10
} > "$OUT/07_ferramentas_aa.txt"

ls -la "$OUT"
echo "SHOTS OK"
