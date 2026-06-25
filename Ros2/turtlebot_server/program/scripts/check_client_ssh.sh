#!/usr/bin/env bash
set -e
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
JSON="$PROJECT_ROOT/program/json/client_info.json"
IP=$(jq -er '.robot_command_client.ssh.ip // .robot_command_client.ip' "$JSON")
USER=$(jq -er '.robot_command_client.ssh.user' "$JSON")
PORT=$(jq -er '.robot_command_client.ssh.port' "$JSON")
TIMEOUT=$(jq -er '.robot_command_client.ssh.connect_timeout' "$JSON")
ssh -p "$PORT" -o BatchMode=yes -o ConnectTimeout="$TIMEOUT" "$USER@$IP" 'echo client_ssh_ok'
