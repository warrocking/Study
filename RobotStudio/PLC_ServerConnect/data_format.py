# data_format.py
#
# Decides how typed input becomes bytes on the wire, and how bytes coming
# back get shown to you. tcp_connection.py never has to know about any of
# this - it just moves bytes. Pick a format at runtime with choose_format().
#
# Three formats:
#   1) PlainTextFormat  - raw string in/out, same style as the ABB robot's
#                          "11"/"22"/"qq" commands. Works with TcpConnection
#                          directly (encode -> send_bytes -> receive_bytes -> decode).
#   2) JsonFormat        - newline-delimited JSON, same style as the turtlebot
#                          fleet_protocol.py contract. Also works with
#                          TcpConnection directly. Field names are checked
#                          against database.json (warning only, not blocking).
#   3) McProtocolFormat  - MELSEC MC Protocol (SLMP) for real PLC device
#                          read/write. This one does NOT go through
#                          TcpConnection.send_bytes/receive_bytes: MC Protocol
#                          needs an exact binary frame (subheader, command
#                          code, device code, etc.), and hand-building those
#                          bytes from scratch risks toggling the wrong bit on
#                          live equipment (press/gripper are on this PLC).
#                          So it uses the pymcprotocol library, which owns its
#                          own socket, instead of raw send_bytes/receive_bytes.

import json
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "database.json"


class PlainTextFormat:
    """Raw string in, raw string out. No structure enforced."""

    def encode(self, text: str) -> bytes:
        return text.encode("ascii", errors="replace")

    def decode(self, raw: bytes) -> str:
        return raw.decode("ascii", errors="replace")


class JsonFormat:
    """Newline-delimited JSON, checked against database.json's field list."""

    def __init__(self):
        self.schema = self._load_schema()

    def _load_schema(self) -> dict:
        if DATABASE_PATH.exists():
            with open(DATABASE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def encode(self, text: str) -> bytes:
        data = json.loads(text)
        known_fields = self.schema.get("fields", {})
        for key in data:
            if known_fields and key not in known_fields:
                print(f"  (warning: '{key}' is not listed in database.json - sending anyway)")
        return (json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8")

    def decode(self, raw: bytes):
        text = raw.decode("utf-8", errors="replace").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}


class McProtocolFormat:
    """
    Structured PLC device access via MC Protocol (SLMP), using pymcprotocol.
    Owns its own connection (ip/port asked and connected here) instead of
    going through TcpConnection - see the module docstring above for why.
    """

    def __init__(self, label):
        self.label = label
        self.ip = None
        self.port = None
        self.client = None

    def ask(self):
        self.ip = input(f"[{self.label}] IP address: ").strip()
        while True:
            raw_port = input(f"[{self.label}] Port: ").strip()
            try:
                self.port = int(raw_port)
                break
            except ValueError:
                print(f"  '{raw_port}' is not a valid port number, try again.")

    def connect(self):
        import pymcprotocol  # imported lazily so plain/json modes don't need it installed

        self.client = pymcprotocol.Type3E()
        self.client.setaccessopt(commtype="binary")  # switch to "ascii" if the target is set to ASCII
        self.client.connect(self.ip, self.port)

    def read_bits(self, device: str, size: int = 1):
        return self.client.batchread_bitunits(headdevice=device, readsize=size)

    def write_bits(self, device: str, values: list):
        self.client.batchwrite_bitunits(headdevice=device, values=values)

    def read_words(self, device: str, size: int = 1):
        return self.client.batchread_wordunits(headdevice=device, readsize=size)

    def write_words(self, device: str, values: list):
        self.client.batchwrite_wordunits(headdevice=device, values=values)

    def result(self):
        print(f"\n--- [{self.label}] result (MC Protocol) ---")
        print(f"  target    : {self.ip}:{self.port}")
        print(f"  connected : {self.client is not None}")

    def close(self):
        if self.client:
            self.client.close()
            self.client = None


def choose_format(label: str):
    """
    Ask which data format to use for this connection.
    Returns (kind, format_instance):
      kind == "plain"       -> format_instance is a PlainTextFormat, use with TcpConnection
      kind == "json"        -> format_instance is a JsonFormat, use with TcpConnection
      kind == "mcprotocol"  -> format_instance is None; caller creates McProtocolFormat itself
                                (it manages its own connection, see class docstring)
    """
    print(f"\n[{label}] Choose data format:")
    print("  1) Plain Text  - raw string, like the ABB robot's simple text commands")
    print("  2) JSON        - newline-delimited JSON, checked against database.json")
    print("  3) MC Protocol - structured PLC device read/write (pymcprotocol)")
    choice = input("Select 1/2/3: ").strip()

    if choice == "2":
        return "json", JsonFormat()
    if choice == "3":
        return "mcprotocol", None
    return "plain", PlainTextFormat()
