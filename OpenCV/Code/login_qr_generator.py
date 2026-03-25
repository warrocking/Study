import argparse
import json
import re
from pathlib import Path

try:
    import qrcode
except Exception as exc:
    raise SystemExit(
        "qrcode package is required. Install with: .\\.venv\\Scripts\\python.exe -m pip install qrcode[pil]"
    ) from exc


def resolve_project_root() -> Path:
    # This script is in OpenCV/Code, so parent() is OpenCV
    return Path(__file__).resolve().parent.parent


def get_default_users_path() -> Path:
    return resolve_project_root() / "Resource" / "Data" / "users.json"


def get_default_output_dir() -> Path:
    return resolve_project_root() / "Resource" / "Data" / "LoginQR"


def load_users(users_path: Path) -> list[dict]:
    if not users_path.exists():
        raise FileNotFoundError(f"users.json not found: {users_path}")

    with users_path.open("r", encoding="utf-8-sig") as fp:
        raw = json.load(fp)

    if isinstance(raw, dict):
        users = raw.get("users", [])
    elif isinstance(raw, list):
        users = raw
    else:
        users = []

    normalized: list[dict] = []
    for item in users:
        if not isinstance(item, dict):
            continue
        user_id = str(item.get("id", "")).strip()
        password = str(item.get("password", "")).strip()
        nickname = str(item.get("nickname", "")).strip()
        if user_id and password and nickname:
            normalized.append({"id": user_id, "password": password, "nickname": nickname})

    return normalized


def sanitize_file_name(text: str) -> str:
    text = re.sub(r"[^0-9A-Za-z_.-]+", "_", text)
    text = text.strip("._")
    return text or "user"


def build_payload(user: dict, qr_format: str) -> str:
    user_id = user["id"]
    password = user["password"]
    nickname = user["nickname"]

    if qr_format == "login_pipe":
        return f"LOGIN|{user_id}|{password}|{nickname}"
    if qr_format == "pipe":
        return f"{user_id}|{password}|{nickname}"
    if qr_format == "json":
        return json.dumps(
            {"id": user_id, "password": password, "nickname": nickname},
            ensure_ascii=False,
            separators=(",", ":"),
        )

    raise ValueError(f"Unsupported format: {qr_format}")


def save_qr_image(payload: str, output_file: Path, box_size: int, border: int) -> None:
    qr_obj = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr_obj.add_data(payload)
    qr_obj.make(fit=True)

    image = qr_obj.make_image(fill_color="black", back_color="white")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_file)


def verify_with_opencv(image_file: Path, expected_payload: str) -> tuple[bool, str]:
    try:
        import cv2
    except Exception:
        return False, "cv2 import failed"

    frame = cv2.imread(str(image_file), cv2.IMREAD_COLOR)
    if frame is None:
        return False, "image read failed"

    detector = cv2.QRCodeDetector()
    decoded_text, points, _ = detector.detectAndDecode(frame)
    if points is None or not decoded_text:
        return False, "decode failed"

    if decoded_text.strip() != expected_payload.strip():
        return False, f"decoded mismatch: {decoded_text}"

    return True, decoded_text


def generate_for_user(
    user: dict,
    output_dir: Path,
    qr_format: str,
    box_size: int,
    border: int,
    verify: bool,
) -> tuple[Path, str, bool, str]:
    payload = build_payload(user, qr_format)

    safe_id = sanitize_file_name(user["id"])
    safe_nick = sanitize_file_name(user["nickname"])
    output_file = output_dir / f"login_qr_{safe_id}_{safe_nick}.png"

    save_qr_image(payload, output_file, box_size=box_size, border=border)

    if verify:
        ok, msg = verify_with_opencv(output_file, payload)
        return output_file, payload, ok, msg

    return output_file, payload, True, "verify skipped"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate login QR code images for portfolio.py login flow"
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--all",
        action="store_true",
        help="Generate QR codes for all users in users.json",
    )
    mode_group.add_argument(
        "--single",
        action="store_true",
        help="Generate QR code for a single user (--id --password --nickname)",
    )

    parser.add_argument(
        "--users-file",
        type=Path,
        default=get_default_users_path(),
        help="Path to users.json (default: Resource/Data/users.json)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=get_default_output_dir(),
        help="Output folder for PNG files (default: Resource/Data/LoginQR)",
    )

    parser.add_argument("--id", dest="user_id", default="", help="Single mode user id")
    parser.add_argument("--password", default="", help="Single mode password")
    parser.add_argument("--nickname", default="", help="Single mode nickname")

    parser.add_argument(
        "--format",
        choices=["login_pipe", "pipe", "json"],
        default="login_pipe",
        help="QR payload format. login_pipe is recommended for portfolio.py",
    )
    parser.add_argument("--box-size", type=int, default=10, help="QR box size")
    parser.add_argument("--border", type=int, default=4, help="QR border size")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify generated PNG by decoding once with OpenCV",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.single:
        if not args.user_id or not args.password or not args.nickname:
            raise SystemExit("Single mode requires --id --password --nickname")
        users = [{"id": args.user_id, "password": args.password, "nickname": args.nickname}]
    else:
        users = load_users(args.users_file)
        if not users:
            raise SystemExit(f"No valid users found in: {args.users_file}")

    print(f"[INFO] users: {len(users)}")
    print(f"[INFO] output: {args.output_dir}")
    print(f"[INFO] format: {args.format}")

    success_count = 0
    for index, user in enumerate(users, start=1):
        output_file, payload, ok, verify_msg = generate_for_user(
            user,
            output_dir=args.output_dir,
            qr_format=args.format,
            box_size=args.box_size,
            border=args.border,
            verify=args.verify,
        )

        masked_pw = "*" * len(user["password"])
        print(
            f"[{index}] id={user['id']} pw={masked_pw} nickname={user['nickname']} -> {output_file}"
        )
        if args.verify:
            print(f"    verify: {'OK' if ok else 'FAIL'} ({verify_msg})")
        # payload is useful for debugging; print only on demand
        # print(f"    payload: {payload}")

        if ok:
            success_count += 1

    print(f"[DONE] success={success_count}/{len(users)}")


if __name__ == "__main__":
    main()
