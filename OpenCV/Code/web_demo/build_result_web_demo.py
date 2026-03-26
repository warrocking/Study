import base64
import json
import urllib.parse
from pathlib import Path

try:
    import qrcode
except Exception:
    qrcode = None

ROOT = Path(r"C:\Study\OpenCV")
RESULT_DIR = ROOT / "Resource" / "Data" / "GameResult"
DEMO_DIR = ROOT / "Code" / "web_demo"
VIEWER_PATH = DEMO_DIR / "result_viewer.html"


def pick_latest_result() -> Path | None:
    files = sorted(RESULT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def encode_payload(obj: dict) -> str:
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    b64 = base64.urlsafe_b64encode(raw).decode("ascii")
    return b64.rstrip("=")


def file_url(path: Path) -> str:
    return path.resolve().as_uri()


def main() -> None:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    latest = pick_latest_result()
    if latest is None:
        print("[ERROR] No result json found in:", RESULT_DIR)
        return

    with latest.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    packed = encode_payload(payload)
    url = f"{file_url(VIEWER_PATH)}?d={urllib.parse.quote(packed)}"

    (DEMO_DIR / "latest_payload.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DEMO_DIR / "latest_result_url.txt").write_text(url, encoding="utf-8")

    preview_html = f"""<!DOCTYPE html>
<html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Result Preview</title>
<style>body{{font-family:Segoe UI,sans-serif;background:#111827;color:#e5e7eb;margin:0;padding:20px}}.box{{max-width:860px;margin:0 auto;background:#1f2937;border:1px solid #374151;border-radius:12px;padding:18px}}a{{color:#22d3ee}}pre{{background:#0f172a;padding:12px;border-radius:8px;overflow:auto}}</style>
</head><body><div class=\"box\">
<h1>Latest Result Preview</h1>
<p><b>Source file:</b> {latest.name}</p>
<p><b>Viewer link:</b> <a href=\"{url}\">Open Viewer</a></p>
<pre>{json.dumps(payload, ensure_ascii=False, indent=2)}</pre>
</div></body></html>"""
    (DEMO_DIR / "result_preview_latest.html").write_text(preview_html, encoding="utf-8")

    if qrcode is not None:
        img = qrcode.make(url)
        img.save(DEMO_DIR / "latest_result_url_qr.png")
        print("[OK] QR image:", DEMO_DIR / "latest_result_url_qr.png")
    else:
        print("[WARN] qrcode package not installed, skip QR image")

    print("[OK] Latest result:", latest)
    print("[OK] Viewer html:", VIEWER_PATH)
    print("[OK] Preview html:", DEMO_DIR / "result_preview_latest.html")
    print("[OK] URL text:", DEMO_DIR / "latest_result_url.txt")
    print("[URL]\n" + url)


if __name__ == "__main__":
    main()
