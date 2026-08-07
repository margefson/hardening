#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

# Ensure DNS
if ! getent hosts deb.debian.org >/dev/null 2>&1; then
  echo "nameserver 8.8.8.8" > /etc/resolv.conf
  echo "nameserver 1.1.1.1" >> /etc/resolv.conf
fi

echo "=== DNS ==="
getent hosts deb.debian.org || true

# Mount securityfs / selinuxfs
mkdir -p /sys/kernel/security
mountpoint -q /sys/kernel/security || mount -t securityfs securityfs /sys/kernel/security
mkdir -p /sys/fs/selinux
mountpoint -q /sys/fs/selinux || mount -t selinuxfs selinuxfs /sys/fs/selinux || true

echo "=== LSM ==="
cat /sys/kernel/security/lsm
ls /sys/fs/selinux | head

echo "=== APT UPDATE ==="
apt-get update -qq

echo "=== INSTALL SELINUX (stage 1 utils) ==="
apt-get install -y selinux-utils policycoreutils checkpolicy

echo "=== INSTALL SELINUX (stage 2 policy + semanage) ==="
apt-get install -y selinux-policy-default policycoreutils-python-utils semanage-utils selinux-basics

echo "=== PACKAGES ==="
dpkg -l | grep -iE 'selinux|policycore|semanage' | head -40

echo "INSTALL DONE"
