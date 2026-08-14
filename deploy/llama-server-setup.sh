#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run this with sudo." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNITS=("generative-server.service" "embedding-server.service" "api-server.service")
ENV_FILES=("localrag-server.env")

mkdir -p /etc/default /opt/localrag/models

for u in "${UNITS[@]}"; do
  cp "$SCRIPT_DIR/$u" /etc/systemd/system/
done

for env_file in "${ENV_FILES[@]}"; do
  cp "$SCRIPT_DIR/$env_file" "/etc/default/$env_file"
done

systemctl daemon-reload

for u in "${UNITS[@]}"; do
  systemctl enable --now "$u"
done

echo "Installed. Check status with:"
echo "  systemctl status generative-server"
echo "  systemctl status embedding-server"
echo "  systemctl status api-server"
echo "Edit /etc/default/localrag-generative, /etc/default/localrag-embedding, and /etc/default/api-server to change settings."
