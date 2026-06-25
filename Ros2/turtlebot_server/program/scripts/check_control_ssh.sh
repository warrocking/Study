#!/usr/bin/env bash
set -e
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
JSON="$PROJECT_ROOT/program/json/control_info.json"
IP=$(jq -er '.control_ui.ip' "$JSON")
USER=$(jq -er '.control_ui.user' "$JSON")
PORT=$(jq -er '.control_ui.ssh.port' "$JSON")
TIMEOUT=$(jq -er '.control_ui.ssh.connect_timeout' "$JSON")
ssh -p "$PORT" -o BatchMode=yes -o ConnectTimeout="$TIMEOUT" "$USER@$IP" 'echo control_ssh_ok'
