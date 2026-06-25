#!/usr/bin/env bash
set -e
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
JSON="$PROJECT_ROOT/program/json/client_info.json"
IP=$(jq -er '.robot_command_client.ip' "$JSON")
PORT=$(jq -er '.robot_command_client.data_control_port' "$JSON")
nc -vz -w 3 "$IP" "$PORT"
