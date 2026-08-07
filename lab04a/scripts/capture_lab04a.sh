#!/bin/bash
set +e
OUT=/mnt/d/MMB/workspace/hardening/lab04a/evidencias
mkdir -p "$OUT/shots" "$OUT/raw"

{
  echo "=== IDENTIDADE DO AMBIENTE ==="
  hostname
  date
  cat /etc/os-release | head -10
  uname -a
  echo
  echo "=== LSM / KERNEL ==="
  cat /sys/kernel/security/lsm 2>&1 || echo "LSM path indisponivel"
  ls /sys/module/apparmor 2>&1 | head -5
  lsmod 2>/dev/null | grep -iE 'apparmor|selinux' || echo "Nenhum modulo apparmor/selinux carregado"
  echo
  echo "=== PACOTES MAC ==="
  dpkg -l | grep -iE 'apparmor|selinux' | head -30
  echo
  echo "=== SELINUX (expectativa: ausente no Debian) ==="
  command -v sestatus || echo "sestatus: NAO INSTALADO"
  command -v getenforce || echo "getenforce: NAO INSTALADO"
  command -v restorecon || echo "restorecon: NAO INSTALADO"
  command -v semanage || echo "semanage: NAO INSTALADO"
  sestatus 2>&1 | head -20
  getenforce 2>&1
  echo
  echo "=== ls -Z / etc ==="
  ls -lZ / 2>&1 | head -25
  ls -lZ /etc 2>&1 | head -15
  echo
  echo "=== ps -Z (amostra) ==="
  ps -eZ 2>&1 | head -25
  echo
  echo "=== APPARMOR STATUS ==="
  systemctl status apparmor --no-pager 2>&1 | head -25
  aa-status 2>&1
  echo
  echo "=== PERFIS EM /etc/apparmor.d ==="
  ls /etc/apparmor.d 2>&1 | head -40
  echo "total profiles files:" $(ls /etc/apparmor.d 2>/dev/null | wc -l)
  echo
  echo "=== EXEMPLO DE PERFIL (usr.bin.man) ==="
  head -40 /etc/apparmor.d/usr.bin.man 2>&1 || head -40 $(ls /etc/apparmor.d/* 2>/dev/null | head -1)
  echo
  echo "=== HELP FERRAMENTAS APPARMOR ==="
  aa-enforce --help 2>&1 | head -15
  aa-complain --help 2>&1 | head -15
  aa-logprof --help 2>&1 | head -15
  aa-genprof --help 2>&1 | head -15
  echo
  echo "=== DONE ==="
} | tee "$OUT/raw/lab04a_full.txt"
