# main.py
#
# Entry point - this is the file to keep editing as needs change.
# tcp_connection.py and data_format.py are the stable building blocks;
# this file just decides the order things happen in.
#
# Run (VSCode integrated terminal, PowerShell):
#     python main.py

from tcp_connection import TcpConnection
from data_format import choose_format, McProtocolFormat


def ask_network_count() -> int:
    while True:
        raw = input("How many networks do you want to connect to?: ").strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("Enter a positive integer.")


def setup_connections(count):
    """
    Pre-connect phase for all N connections: for each one, pick a data
    format and enter its IP/port. Nothing is actually connected yet - this
    only decides, per connection, what it will be and how it will talk.
    Returns a list of (label, kind, bundle) tuples for run_connections().
    """
    setups = []
    for i in range(count):
        label = f"conn{i + 1}"
        print(f"\n=== [{label}] setup ===")
        kind, fmt = choose_format(label)
        if kind == "mcprotocol":
            mc = McProtocolFormat(label)
            mc.ask()
            setups.append((label, kind, mc))
        else:
            conn = TcpConnection(label)
            conn.ask()
            setups.append((label, kind, (conn, fmt)))
    return setups


def run_connections(setups):
    """Connecting/session phase: actually connect and interact, one at a time, in setup order."""
    for label, kind, bundle in setups:
        print(f"\n=== [{label}] connect ===")
        if kind == "mcprotocol":
            run_mcprotocol_session(bundle)
        else:
            conn, fmt = bundle
            run_text_or_json_session(conn, fmt)


def run_text_or_json_session(conn, fmt):
    if not conn.connect():
        conn.result()
        return

    while True:
        user_input = input(f"[{conn.label}] Enter command/value to send (or 'exit'): ")
        if user_input.strip().lower() == "exit":
            break
        try:
            payload = fmt.encode(user_input)
        except Exception as e:
            print(f"  encode error: {e}")
            continue
        conn.send_bytes(payload)
        raw = conn.receive_bytes()
        print(f"  received: {fmt.decode(raw)}")

    conn.result()
    conn.close()


def run_mcprotocol_session(fmt):
    fmt.connect()

    while True:
        action = input(f"[{fmt.label}] read/write/exit: ").strip().lower()
        if action == "exit":
            break
        if action not in ("read", "write"):
            print("  unknown command, type read/write/exit")
            continue

        device = input(f"[{fmt.label}] device address (e.g. X1006): ").strip()
        if action == "read":
            values = fmt.read_bits(device, size=1)
            print(f"  {device} = {values}")
        else:
            raw_value = input(f"[{fmt.label}] value to write (0/1): ").strip()
            fmt.write_bits(device, [int(raw_value)])
            print(f"  wrote {raw_value} to {device}")

    fmt.result()
    fmt.close()


def main():
    count = ask_network_count()
    setups = setup_connections(count)
    run_connections(setups)


if __name__ == "__main__":
    main()
