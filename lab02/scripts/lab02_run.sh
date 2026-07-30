#!/bin/bash
# Lab 02 - Execucao completa: inventario, correcoes e validacoes
set -euo pipefail
OUT=/mnt/d/MMB/workspace/hardening/lab02/evidencias/lab02_evidence.txt
exec >"$OUT" 2>&1

log() { echo; echo "===== $* ====="; date '+%Y-%m-%d %H:%M:%S'; }

log "INICIO LAB 02 - hostname=$(hostname) user=$(whoami)"

log "MISSAO 1 - INVENTARIO INICIAL"
echo "--- whoami / who ---"
whoami; who || true
echo "--- passwd (humanos e relevantes) ---"
getent passwd | awk -F: '$3>=1000 || $1 ~ /^(root|backup|ana|carlos|maria|paulo|temporario)$/ {print}'
echo "--- todos passwd ---"
getent passwd
echo "--- groups relevantes ---"
getent group | egrep 'sudo|desenvolvimento|infraestrutura|financeiro|auditoria|adm|machado' || true
echo "--- id machado root ---"
id machado; id root

log "CRIACAO DE USUARIOS E GRUPOS (cenario AmazonTech WEB-01)"
# Grupos corporativos
for g in desenvolvimento infraestrutura financeiro auditoria; do
  if getent group "$g" >/dev/null; then
    echo "Grupo ja existia: $g"
  else
    groupadd "$g"
    echo "Grupo criado: $g"
  fi
done

# Usuarios corporativos (exceto backup sistema)
create_user() {
  local u=$1 shell=${2:-/bin/bash}
  if id "$u" >/dev/null 2>&1; then
    echo "Usuario ja existia: $u"
  else
    useradd -m -s "$shell" "$u"
    echo "Usuario criado: $u"
  fi
  echo "${u}:Lab02@AmazonTech" | chpasswd
}

create_user ana
create_user carlos
create_user maria
create_user paulo
create_user temporario

# Conta backup ja existe no Debian (UID 34). Garantir shell nologin no final.
if id backup >/dev/null 2>&1; then
  echo "Conta backup (sistema) ja existe: $(getent passwd backup)"
else
  useradd -r -s /usr/sbin/nologin -d /var/backups backup
  echo "Conta backup criada"
fi

log "SIMULACAO DE INCONSISTENCIAS (situacao anterior da auditoria)"
# Associa corretamente E simula inconsistencias para depois corrigir
usermod -aG desenvolvimento ana || true
usermod -aG infraestrutura ana || true   # inconsistencia
usermod -aG infraestrutura carlos || true
usermod -aG sudo carlos || true
usermod -aG financeiro maria || true
usermod -aG desenvolvimento maria || true # inconsistencia
usermod -aG auditoria paulo || true
usermod -aG sudo ana || true              # inconsistencia
usermod -aG sudo backup || true           # inconsistencia
usermod -aG sudo temporario || true       # inconsistencia

echo "--- situacao ANTERIOR (apos inconsistencias simuladas) ---"
for u in ana carlos maria paulo backup temporario machado; do
  echo -n "$u: "; id "$u" 2>/dev/null || echo "N/A"
done
echo "sudo group: $(getent group sudo)"

log "MISSAO 2 - ORGANIZACAO (remocao de associacoes indevidas)"
gpasswd -d ana infraestrutura || true
gpasswd -d maria desenvolvimento || true
# backup nao deve ter grupo administrativo - removido na missao 3

echo "--- apos limpeza parcial de grupos ---"
for u in ana carlos maria paulo backup; do id "$u"; done
getent group desenvolvimento
getent group infraestrutura
getent group financeiro
getent group auditoria

log "MISSAO 3 - PRIVILEGIOS ADMINISTRATIVOS"
echo "--- sudo ANTES da correcao ---"
getent group sudo
gpasswd -d ana sudo || true
gpasswd -d backup sudo || true
gpasswd -d temporario sudo || true
# manter carlos e machado
passwd -l temporario || true
usermod -s /usr/sbin/nologin backup || true

echo "--- sudo DEPOIS ---"
getent group sudo
echo "--- status contas ---"
passwd -S temporario || true
passwd -S backup || true
getent passwd backup
for u in ana carlos maria paulo backup temporario; do id "$u"; done

log "MISSAO 4 - DIRETORIOS E PERMISSOES"
for d in /projetos /financeiro /auditoria /infraestrutura; do
  if [ -d "$d" ]; then echo "Diretorio ja existia: $d"; else mkdir "$d"; echo "Criado: $d"; fi
done

chown ana:desenvolvimento /projetos
chown maria:financeiro /financeiro
chown paulo:auditoria /auditoria
chown carlos:infraestrutura /infraestrutura

chmod 750 /projetos
chmod 770 /financeiro
chmod 750 /auditoria
chmod 750 /infraestrutura

# Arquivos de teste
sudo -u ana touch /projetos/projeto-web.txt
sudo -u maria touch /financeiro/relatorio-financeiro.txt
# garantir legivel pelo grupo/ACL
chmod 640 /financeiro/relatorio-financeiro.txt
chown maria:financeiro /financeiro/relatorio-financeiro.txt
sudo -u paulo touch /auditoria/parecer.txt
sudo -u carlos touch /infraestrutura/inventario.txt

echo "--- ls -ld ---"
ls -ld /projetos /financeiro /auditoria /infraestrutura
echo "--- arquivos ---"
ls -l /projetos /financeiro /auditoria /infraestrutura

echo "--- testes autorizados ---"
sudo -u ana ls /projetos && echo "ana->projetos OK" || echo "ana->projetos FAIL"
sudo -u maria ls /financeiro && echo "maria->financeiro OK" || echo "maria->financeiro FAIL"
sudo -u paulo ls /auditoria && echo "paulo->auditoria OK" || echo "paulo->auditoria FAIL"
sudo -u carlos ls /infraestrutura && echo "carlos->infra OK" || echo "carlos->infra FAIL"

echo "--- testes indevidos (esperar Permission denied) ---"
sudo -u ana ls /financeiro 2>&1 || true
sudo -u maria ls /infraestrutura 2>&1 || true
sudo -u paulo ls /projetos 2>&1 || true

log "MISSAO 5 - ACL"
# instalar acl se necessario
if ! command -v setfacl >/dev/null; then
  apt-get install -y acl
fi
echo "--- ACL inicial ---"
ls -ld /financeiro
getfacl /financeiro
echo "paulo antes:"; sudo -u paulo ls /financeiro 2>&1 || true

setfacl -m u:paulo:rx /financeiro
# ACL no arquivo para leitura
setfacl -m u:paulo:r /financeiro/relatorio-financeiro.txt

echo "--- ACL apos concessao ---"
getfacl /financeiro
ls -ld /financeiro
echo "paulo listar:"; sudo -u paulo ls /financeiro 2>&1 || true
echo "paulo ler:"; sudo -u paulo cat /financeiro/relatorio-financeiro.txt 2>&1 || true
echo "paulo escrever:"; sudo -u paulo touch /financeiro/teste-auditoria.txt 2>&1 || true
echo "grupos paulo:"; id paulo

echo "--- remocao ACL ---"
setfacl -x u:paulo /financeiro
setfacl -x u:paulo /financeiro/relatorio-financeiro.txt || true
getfacl /financeiro
echo "paulo apos remocao:"; sudo -u paulo ls /financeiro 2>&1 || true

log "MISSAO 6 - SUDO"
echo "--- sudo -l machado ---"
sudo -l || true
echo "--- sudo -l -U carlos ---"
sudo -l -U carlos || true
echo "--- sudo -l -U ana ---"
sudo -l -U ana || true
echo "--- sudo -l -U maria ---"
sudo -l -U maria || true
echo "--- sudo -l -U paulo ---"
sudo -l -U paulo || true
echo "--- trecho sudoers ---"
grep -E '^%sudo|^root|^Defaults' /etc/sudoers || true
ls /etc/sudoers.d/ || true
echo "--- teste systemctl cron ---"
systemctl status cron --no-pager 2>&1 | head -15 || true
echo "--- sudo -k / ls /root ---"
# como root ja, apenas documentar comportamento esperado
echo "(executado como root na automacao; no uso interativo sudo -k exige reautenticacao)"

log "MISSAO 7 - AUDITORIA FINAL"
echo "--- identidades finais ---"
for u in ana carlos maria paulo backup temporario machado; do
  echo -n "$u: "; id "$u"; getent passwd "$u"
done
echo "--- grupos corporativos ---"
for g in desenvolvimento infraestrutura financeiro auditoria sudo; do
  getent group "$g"
done
echo "--- diretorios ---"
ls -ld /projetos /financeiro /auditoria /infraestrutura
getfacl /financeiro
echo "--- passwd -S temporario ---"
passwd -S temporario
echo "--- shell backup ---"
getent passwd backup

log "FIM LAB 02"
