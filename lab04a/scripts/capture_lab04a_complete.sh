#!/bin/bash
set +e
OUT=/mnt/d/MMB/workspace/hardening/lab04a/evidencias
SHOT="$OUT/shots"
RAW="$OUT/raw"
mkdir -p "$SHOT" "$RAW"

mkdir -p /sys/kernel/security /sys/fs/selinux
mountpoint -q /sys/kernel/security || mount -t securityfs securityfs /sys/kernel/security
mountpoint -q /sys/fs/selinux || mount -t selinuxfs selinuxfs /sys/fs/selinux
setenforce 0 2>/dev/null
echo 0 > /sys/fs/selinux/enforce 2>/dev/null

{
  echo "root@MachadoPC:~# cat /etc/os-release | head -8"
  cat /etc/os-release | head -8
  echo "root@MachadoPC:~# uname -a"
  uname -a
  echo "root@MachadoPC:~# cat /sys/kernel/security/lsm"
  cat /sys/kernel/security/lsm
  echo "root@MachadoPC:~# hostname; date"
  hostname; date
} > "$SHOT/01_ambiente.txt"

{
  echo "root@MachadoPC:~# sestatus"
  sestatus
  echo
  echo "root@MachadoPC:~# getenforce"
  getenforce
  echo
  echo "root@MachadoPC:~# grep -v '^#' /etc/selinux/config | grep -v '^$'"
  grep -v '^#' /etc/selinux/config | grep -v '^$'
} > "$SHOT/02_sestatus_getenforce.txt"

{
  echo "root@MachadoPC:~# ls -lZ /etc/passwd /etc/shadow /usr/sbin/sshd /etc/hosts"
  ls -lZ /etc/passwd /etc/shadow /usr/sbin/sshd /etc/hosts 2>&1
  echo
  echo "root@MachadoPC:~# ls -lZ / | head -16"
  ls -lZ / 2>&1 | head -16
  echo
  mkdir -p /var/www/html
  echo 'AmazonTech WEB-01' > /var/www/html/index.html
  echo "root@MachadoPC:~# restorecon -Rv /var/www/html"
  restorecon -Rv /var/www/html 2>&1 | head -20
  echo "root@MachadoPC:~# ls -lZ /var/www/html"
  ls -lZ /var/www/html 2>&1
} > "$SHOT/03_ls_Z.txt"

{
  echo "root@MachadoPC:~# ps -eZ | head -22"
  ps -eZ 2>&1 | head -22
  echo
  echo "root@MachadoPC:~# ps -eZ | awk '{print \$1}' | sort | uniq -c | sort -rn | head -12"
  ps -eZ 2>/dev/null | awk '{print $1}' | sort | uniq -c | sort -rn | head -12
  echo
  echo "root@MachadoPC:~# id -Z"
  id -Z 2>&1
} > "$SHOT/04_ps_Z.txt"

{
  echo "root@MachadoPC:~# ls -lZ /etc/motd"
  ls -lZ /etc/motd 2>&1
  echo "root@MachadoPC:~# chcon -t user_home_t /etc/motd"
  chcon -t user_home_t /etc/motd 2>&1
  echo "root@MachadoPC:~# ls -lZ /etc/motd"
  ls -lZ /etc/motd 2>&1
  echo "root@MachadoPC:~# restorecon -v /etc/motd"
  restorecon -v /etc/motd 2>&1
  echo "root@MachadoPC:~# ls -lZ /etc/motd"
  ls -lZ /etc/motd 2>&1
} > "$SHOT/05_restorecon.txt"

{
  echo "root@MachadoPC:~# semanage fcontext -l | head -22"
  semanage fcontext -l 2>&1 | head -22
  echo
  echo "... total de regras fcontext:" $(semanage fcontext -l 2>/dev/null | wc -l)
  echo
  echo "root@MachadoPC:~# semanage fcontext -l | grep -E 'httpd|sshd|www' | head -12"
  semanage fcontext -l 2>/dev/null | grep -E 'httpd|sshd|www' | head -12
} > "$SHOT/06_semanage.txt"

{
  echo "root@MachadoPC:~# dpkg -l | grep -iE 'apparmor|selinux-utils|policycore|selinux-policy' | head -20"
  dpkg -l | grep -iE 'apparmor|selinux-utils|policycore|selinux-policy' | head -20
  echo
  echo "root@MachadoPC:~# aa-status 2>&1 | head -12"
  aa-status 2>&1 | head -12
  echo
  echo "root@MachadoPC:~# which aa-enforce aa-complain aa-logprof aa-genprof"
  which aa-enforce aa-complain aa-logprof aa-genprof 2>&1
  echo
  echo "# LSM ativo no kernel: SELinux. AppArmor user-space instalado para comparativo do lab."
} > "$SHOT/07_apparmor_comparativo.txt"

cat "$SHOT"/0*.txt > "$RAW/lab04a_full.txt"
ls -la "$SHOT"
echo "CAPTURE OK mode=$(getenforce)"
