#!/usr/bin/env bash
set -e
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
cd "$PROJECT_ROOT/program/code"
python3 -m py_compile \
  server_manager.py \
  config_loader.py \
  fleet_protocol.py \
  fleet_server_main.py \
  control_connection_manager.py \
  client_connection_manager.py \
  command_router.py \
  data_transfer_manager.py \
  data_log_manager.py \
  emergency_supervisor.py \
  opencv_manager.py
python3 -m py_compile "$PROJECT_ROOT/tests/mock_external/mock_robot_command_client.py"
echo compile_ok
