import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(r"C:\Study\OpenCV")
DEMO_DIR = ROOT / "Code" / "web_demo"
BUILD_SCRIPT = DEMO_DIR / "build_result_web_demo_lan.py"
URL_FILE = DEMO_DIR / "latest_result_url_lan.txt"
PORT = 8765


def run_build() -> bool:
    result = subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(DEMO_DIR))
    return result.returncode == 0


def read_url() -> str:
    return URL_FILE.read_text(encoding="utf-8").strip()


def main() -> None:
    if not run_build():
        print("[ERROR] Failed to build LAN URL / QR")
        return

    try:
        url = read_url()
    except Exception as exc:
        print("[ERROR] Failed to read URL file:", exc)
        return

    print("\n[HOTSPOT READY]")
    print("1) Scan: C:/Study/OpenCV/Code/web_demo/scan_this_phone_qr.png")
    print("2) Or open this URL on phone:")
    print(url)
    print("\n[SERVER]")
    print("- Starting HTTP server at 0.0.0.0:8765")
    print("- Keep this window open. Press Ctrl+C to stop.\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "http.server",
                str(PORT),
                "--bind",
                "0.0.0.0",
                "--directory",
                str(DEMO_DIR),
            ],
            cwd=str(DEMO_DIR),
        )
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped")


if __name__ == "__main__":
    main()
