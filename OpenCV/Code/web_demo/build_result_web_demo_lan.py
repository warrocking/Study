import base64
import json
import re
import socket
import subprocess
import urllib.parse
from pathlib import Path

try:
    import qrcode
except Exception:
    qrcode = None

ROOT = Path(r"C:\Study\OpenCV")
RESULT_DIR = ROOT / "Resource" / "Data" / "GameResult"
DEMO_DIR = ROOT / "Code" / "web_demo"
VIEWER_FILE = "result_viewer.html"
PORT = 8765


def pick_latest_result() -> Path | None:
    files = sorted(RESULT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def encode_payload(obj: dict) -> str:
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    b64 = base64.urlsafe_b64encode(raw).decode("ascii")
    return b64.rstrip("=")


def is_valid_ipv4(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return False
    return all(0 <= n <= 255 for n in nums)


def is_private_ipv4(ip: str) -> bool:
    if not is_valid_ipv4(ip):
        return False
    a, b, _, _ = [int(x) for x in ip.split(".")]
    if a == 10:
        return True
    if a == 172 and 16 <= b <= 31:
        return True
    if a == 192 and b == 168:
        return True
    return False


def ip_priority(ip: str) -> int:
    if ip.startswith("172.20.10."):
        return 120
    if ip.startswith("192.168."):
        return 110
    if ip.startswith("10."):
        return 100
    if ip.startswith("172."):
        return 90
    return 10


def get_route_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        if is_valid_ipv4(ip) and not ip.startswith("127.") and not ip.startswith("169.254."):
            return ip
    except Exception:
        pass
    finally:
        sock.close()
    return ""


def collect_ip_candidates() -> list[str]:
    candidates: list[str] = []

    route_ip = get_route_ip()
    if route_ip:
        candidates.append(route_ip)

    try:
        host_infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
        for info in host_infos:
            ip = info[4][0]
            candidates.append(ip)
    except Exception:
        pass

    try:
        output = subprocess.check_output(
            ["ipconfig"], stderr=subprocess.STDOUT, encoding="cp949", errors="ignore"
        )
        for line in output.splitlines():
            if "IPv4" in line:
                match = re.search(r"(\\d{1,3}(?:\\.\\d{1,3}){3})", line)
                if match:
                    candidates.append(match.group(1))
    except Exception:
        pass

    normalized: list[str] = []
    for ip in candidates:
        if not is_valid_ipv4(ip):
            continue
        if ip.startswith("127.") or ip.startswith("169.254."):
            continue
        if ip not in normalized:
            normalized.append(ip)
    return normalized


def get_local_ip() -> str:
    # First priority: route-based IP from active network path.
    route_ip = get_route_ip()
    if route_ip:
        return route_ip

    candidates = collect_ip_candidates()
    private_candidates = [ip for ip in candidates if is_private_ipv4(ip)]

    if private_candidates:
        private_candidates.sort(key=lambda ip: ip_priority(ip), reverse=True)
        return private_candidates[0]

    if candidates:
        return candidates[0]

    return "127.0.0.1"


def main() -> None:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    latest = pick_latest_result()
    if latest is None:
        print("[ERROR] No result json found in:", RESULT_DIR)
        return

    with latest.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    packed = encode_payload(payload)
    ip = get_local_ip()
    lan_url = f"http://{ip}:{PORT}/{VIEWER_FILE}?d={urllib.parse.quote(packed)}"

    (DEMO_DIR / "latest_result_url_lan.txt").write_text(lan_url, encoding="utf-8")
    (DEMO_DIR / "latest_payload.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if qrcode is not None:
        img = qrcode.make(lan_url)
        lan_qr_path = DEMO_DIR / "latest_result_url_qr_lan.png"
        scan_qr_path = DEMO_DIR / "scan_this_phone_qr.png"
        img.save(lan_qr_path)
        img.save(scan_qr_path)
        print("[OK] QR image:", lan_qr_path)
        print("[OK] Phone QR:", scan_qr_path)
    else:
        print("[WARN] qrcode package not installed, skip QR image")

    print("[OK] Latest result:", latest)
    print("[OK] LAN URL file:", DEMO_DIR / "latest_result_url_lan.txt")
    print("[URL]\n" + lan_url)


if __name__ == "__main__":
    main()

