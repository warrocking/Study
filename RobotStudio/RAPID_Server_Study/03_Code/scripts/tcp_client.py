from __future__ import annotations

import argparse
import json
import socket
import uuid


def main() -> None:
    parser = argparse.ArgumentParser(description="Send one framed command to the lab gateway")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9100)
    parser.add_argument("--format", choices=("json", "pipe"), default="pipe")
    args = parser.parse_args()

    command_id = f"py-{uuid.uuid4().hex[:8]}"
    if args.format == "json":
        frame = json.dumps(
            {"version": 1, "id": command_id, "type": "ping", "payload": {}},
            separators=(",", ":"),
        ).encode() + b"\n"
    else:
        frame = f"PING|{command_id}\r\n".encode("ascii")

    with socket.create_connection((args.host, args.port), timeout=3) as client:
        client.sendall(frame)
        reply = client.makefile("rb").readline(8193)
    print(reply.decode("utf-8", "replace").rstrip())


if __name__ == "__main__":
    main()

