#!/usr/bin/env bash
set -e
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
JSON="$PROJECT_ROOT/program/json/server_config.json"
PORT=$(jq -er '.server.control_command_port' "$JSON")
ss -ltnp | grep ":$PORT" || true
