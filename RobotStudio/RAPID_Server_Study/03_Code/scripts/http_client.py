from __future__ import annotations

import argparse
import uuid

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Call the lab FastAPI bridge")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--key", default="lab-only-change-me")
    args = parser.parse_args()

    response = httpx.post(
        f"{args.url.rstrip('/')}/v1/commands",
        headers={"X-Bridge-Key": args.key},
        json={"id": f"http-{uuid.uuid4().hex[:8]}", "type": "ping", "payload": {}},
        timeout=3,
    )
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()

