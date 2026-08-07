#!/bin/bash
set +e
export DEBIAN_FRONTEND=noninteractive

mkdir -p /sys/kernel/security
mountpoint -q /sys/kernel/security || mount -t securityfs securityfs /sys/kernel/security
mkdir -p /sys/fs/selinux
mountpoint -q /sys/fs/selinux || mount -t selinuxfs selinuxfs /sys/fs/selinux

echo "=== BEFORE ==="
sestatus 2>&1
getenforce 2>&1
cat /sys/fs/selinux/enforce 2>&1
ls /etc/selinux 2>&1

# Config: permissive first for safe activate
mkdir -p /etc/selinux
if [ ! -f /etc/selinux/config ]; then
  cat > /etc/selinux/config <<'EOF'
# This file controls the state of SELinux on the system.
SELINUX=permissive
SELINUXTYPE=default
EOF
else
  sed -i 's/^SELINUX=.*/SELINUX=permissive/' /etc/selinux/config
  sed -i 's/^SELINUXTYPE=.*/SELINUXTYPE=default/' /etc/selinux/config
fi

echo "=== CONFIG ==="
cat /etc/selinux/config

# Ensure policy file exists
ls -la /etc/selinux/default/policy/ 2>&1 | head -20

# Load policy if not loaded
if [ ! -s /sys/fs/selinux/policy ] || ! sestatus 2>/dev/null | grep -qi 'enabled'; then
  echo "=== LOAD POLICY ==="
  # try load_policy from policycoreutils
  if [ -f /etc/selinux/default/policy/policy.33 ]; then
    load_policy /etc/selinux/default/policy/policy.33 2>&1
  elif [ -f /etc/selinux/default/policy/policy.32 ]; then
    load_policy /etc/selinux/default/policy/policy.32 2>&1
  else
    POL=$(ls /etc/selinux/default/policy/policy.* 2>/dev/null | sort -V | tail -1)
    echo "Using policy: $POL"
    load_policy "$POL" 2>&1
  fi
fi

echo "=== AFTER LOAD ==="
sestatus -v 2>&1 | head -40
getenforce 2>&1

# Keep permissive while labeling key dirs (avoid /mnt WSL)
echo 0 > /sys/fs/selinux/enforce
setenforce 0 2>&1

echo "=== RESTORECON key paths ==="
for p in /etc /usr/bin /usr/sbin /bin /sbin /var /root /home /projetos /financeiro /auditoria /infraestrutura; do
  if [ -e "$p" ]; then
    echo "-- restorecon -Rv $p (sample)"
    restorecon -Rv "$p" 2>&1 | tail -5
  fi
done

echo "=== SAMPLE LABELS ==="
ls -lZ /etc/passwd /etc/shadow /usr/sbin/sshd 2>&1
ls -lZ /var/www/html 2>&1 | head -5
ls -lZ / 2>&1 | head -15

echo "=== SET ENFORCING ==="
setenforce 1 2>&1
echo 1 > /sys/fs/selinux/enforce 2>&1
getenforce 2>&1
sestatus 2>&1

# Update config to enforcing for persistence claim
sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config

echo "=== PS -Z ==="
ps -eZ 2>&1 | head -25

echo "=== SEMANAGE sample ==="
semanage fcontext -l 2>&1 | head -20
echo "... total rules:" $(semanage fcontext -l 2>/dev/null | wc -l)

echo "=== RESTORECON demo on /etc/hosts ==="
ls -lZ /etc/hosts
restorecon -v /etc/hosts 2>&1
ls -lZ /etc/hosts

echo "=== FINAL STATUS ==="
sestatus
getenforce
id -Z 2>&1

echo "ACTIVATE DONE"
