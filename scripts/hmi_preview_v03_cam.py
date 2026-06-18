import json
import socket
import shutil
import subprocess
import glob
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox


CONFIG_FILE = Path("server_hmi_v03_config.json")
LOG_ROOT = Path("logs/server_hmi_v03")

DEFAULT_CONFIG = {
    "server_ip": "192.168.0.78",
    "allowed_client_ip": "192.168.0.137",
    "port": 5000,

    "default_robot": "tb3_1",
    "default_topic": "/cmd_vel",

    "default_lx": 0.05,
    "default_az": 0.0,
    "default_turn_az": 0.5,
    "default_dur": 2.0,
    "default_hz": 10,
    "default_timeout": 5.0,

    "min_free_mb": 100,
    "camera_index": 0
}


# ============================================================
# 공통 함수
# ============================================================

def now_ts():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_time_string():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def load_config():
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            loaded = json.load(f)

        config = dict(DEFAULT_CONFIG)
        config.update(loaded)
        return config

    except Exception:
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)


def save_config(config):
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def ensure_log_dirs():
    (LOG_ROOT / "commands").mkdir(parents=True, exist_ok=True)
    (LOG_ROOT / "system").mkdir(parents=True, exist_ok=True)


def save_json_log(category, prefix, data):
    ensure_log_dirs()

    folder = LOG_ROOT / category
    folder.mkdir(parents=True, exist_ok=True)

    time_text = safe_time_string()
    history_path = folder / f"{prefix}_{time_text}.json"
    latest_path = folder / f"latest_{prefix}.json"

    with history_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with latest_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return history_path, latest_path


def to_float(value, default_value):
    try:
        return float(value)
    except Exception:
        return float(default_value)


def to_int(value, default_value):
    try:
        return int(value)
    except Exception:
        return int(default_value)


def get_local_ip_candidates():
    ips = set()

    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if "." in ip and not ip.startswith("127."):
                ips.add(ip)
    except Exception:
        pass

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        if ip and not ip.startswith("127."):
            ips.add(ip)
        s.close()
    except Exception:
        pass

    return sorted(ips)


def check_port_available(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((ip, int(port)))
        s.close()
        return True, f"{ip}:{port} bind 가능"
    except Exception as e:
        try:
            s.close()
        except Exception:
            pass
        return False, str(e)


def check_client_ping(client_ip):
    if not client_ip:
        return False, "클라이언트 IP가 비어 있음"

    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", client_ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if result.returncode == 0:
            return True, f"{client_ip} ping 성공"

        return False, f"{client_ip} ping 실패"

    except Exception as e:
        return False, f"ping 실행 실패: {e}"


def check_disk_space(path, min_free_mb):
    usage = shutil.disk_usage(path)
    free_mb = usage.free // (1024 * 1024)

    if free_mb >= int(min_free_mb):
        return True, f"저장공간 OK: {free_mb} MB 여유"

    return False, f"저장공간 부족: {free_mb} MB 여유, 최소 {min_free_mb} MB 필요"


def check_json_write():
    ensure_log_dirs()

    data = {
        "v": 3,
        "mt": "server_check",
        "ts": now_ts(),
        "ok": True,
        "msg": "json write test"
    }

    try:
        history_path, latest_path = save_json_log("system", "server_status", data)
        return True, f"JSON 저장 OK: {latest_path}"
    except Exception as e:
        return False, f"JSON 저장 실패: {e}"


# ============================================================
# 카메라 함수
# ============================================================

def get_video_device_numbers():
    devices = []

    for path in sorted(glob.glob("/dev/video*")):
        name = path.replace("/dev/video", "")

        if name.isdigit():
            devices.append(int(name))

    return devices


def test_camera_index(index):
    try:
        import cv2
    except Exception as e:
        return False, f"OpenCV import 실패: {e}", None

    cap = None

    try:
        cap = cv2.VideoCapture(int(index), cv2.CAP_V4L2)

        if not cap.isOpened():
            return False, f"/dev/video{index} 열기 실패", None

        ok, frame = cap.read()

        if not ok or frame is None:
            return False, f"/dev/video{index} 프레임 읽기 실패", None

        h, w = frame.shape[:2]
        return True, f"/dev/video{index} 카메라 OK, frame {w}x{h}", (w, h)

    except Exception as e:
        return False, f"/dev/video{index} 확인 중 오류: {e}", None

    finally:
        if cap is not None:
            cap.release()


def find_available_cameras(max_index=6):
    results = []

    device_numbers = get_video_device_numbers()

    if not device_numbers:
        device_numbers = list(range(max_index + 1))

    checked = set()

    for idx in device_numbers:
        if idx in checked:
            continue

        checked.add(idx)
        ok, msg, size = test_camera_index(idx)

        results.append({
            "index": idx,
            "ok": ok,
            "msg": msg,
            "size": size
        })

    return results


# ============================================================
# JSON v0.3 명령 생성
# ============================================================

def make_ids(seq):
    date_text = datetime.now().strftime("%Y%m%d")
    return f"C{date_text}_{seq:04d}", f"J{date_text}_{seq:04d}"


def make_move_vel_command(seq, robot, topic, lx, az, dur, hz, stop, timeout):
    cmd_id, job_id = make_ids(seq)

    return {
        "v": 3,
        "mt": "cmd",
        "id": cmd_id,
        "ts": now_ts(),
        "job": job_id,
        "to": robot,
        "op": "move_vel",
        "ros": "topic",
        "topic": topic,
        "p": {
            "lx": float(lx),
            "az": float(az),
            "dur": float(dur),
            "hz": int(hz),
            "stop": bool(stop)
        },
        "lim": {
            "timeout": float(timeout)
        }
    }


def make_stop_command(seq, robot, topic, dur, hz, timeout):
    cmd_id, job_id = make_ids(seq)

    return {
        "v": 3,
        "mt": "cmd",
        "id": cmd_id,
        "ts": now_ts(),
        "job": job_id,
        "to": robot,
        "op": "stop",
        "ros": "topic",
        "topic": topic,
        "p": {
            "dur": float(dur),
            "hz": int(hz)
        },
        "lim": {
            "timeout": float(timeout)
        }
    }


def validate_command_v03(cmd):
    required = ["v", "mt", "id", "ts", "job", "to", "op", "ros", "topic", "p"]

    for key in required:
        if key not in cmd:
            return False, f"필수 key 누락: {key}"

    if cmd["v"] != 3:
        return False, "v 값이 3이 아님"

    if cmd["mt"] != "cmd":
        return False, "mt 값이 cmd가 아님"

    if not isinstance(cmd["p"], dict):
        return False, "p는 object여야 함"

    if cmd["op"] == "move_vel":
        for key in ["lx", "az", "dur", "hz", "stop"]:
            if key not in cmd["p"]:
                return False, f"move_vel p.{key} 누락"

    if cmd["op"] == "stop":
        for key in ["dur", "hz"]:
            if key not in cmd["p"]:
                return False, f"stop p.{key} 누락"

    return True, "OK"


# ============================================================
# HMI 클래스
# ============================================================

class ServerHMI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("TurtleBot Server HMI Preview v0.3 - Camera")
        self.geometry("1180x800")
        self.minsize(1050, 700)

        self.config_data = load_config()
        self.command_seq = 1
        self.latest_command = None

        self.camera_cap = None
        self.camera_running = False
        self.camera_image_tk = None

        self.var_server_ip = tk.StringVar(value=str(self.config_data["server_ip"]))
        self.var_client_ip = tk.StringVar(value=str(self.config_data["allowed_client_ip"]))
        self.var_port = tk.StringVar(value=str(self.config_data["port"]))

        self.var_robot = tk.StringVar(value=str(self.config_data["default_robot"]))
        self.var_topic = tk.StringVar(value=str(self.config_data["default_topic"]))

        self.var_lx = tk.StringVar(value=str(self.config_data["default_lx"]))
        self.var_az = tk.StringVar(value=str(self.config_data["default_az"]))
        self.var_turn_az = tk.StringVar(value=str(self.config_data["default_turn_az"]))
        self.var_dur = tk.StringVar(value=str(self.config_data["default_dur"]))
        self.var_hz = tk.StringVar(value=str(self.config_data["default_hz"]))
        self.var_timeout = tk.StringVar(value=str(self.config_data["default_timeout"]))

        self.var_min_free_mb = tk.StringVar(value=str(self.config_data["min_free_mb"]))
        self.var_camera_index = tk.StringVar(value=str(self.config_data["camera_index"]))
        self.var_status = tk.StringVar(value="HMI 준비 중")

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.run_startup_checks()

    # --------------------------------------------------------
    # UI 구성
    # --------------------------------------------------------

    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        title = ttk.Label(
            root,
            text="TurtleBot Server HMI Preview v0.3",
            font=("Arial", 18, "bold")
        )
        title.pack(anchor="w")

        status = ttk.Label(
            root,
            textvariable=self.var_status,
            font=("Arial", 11, "bold")
        )
        status.pack(anchor="w", pady=(0, 8))

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.tab_check = ttk.Frame(notebook, padding=10)
        self.tab_command = ttk.Frame(notebook, padding=10)
        self.tab_camera = ttk.Frame(notebook, padding=10)

        notebook.add(self.tab_check, text="서버 점검")
        notebook.add(self.tab_command, text="명령 생성 HMI")
        notebook.add(self.tab_camera, text="USB 웹캠 확인")

        self._build_check_tab()
        self._build_command_tab()
        self._build_camera_tab()

    def _add_labeled_entry(self, parent, label, variable):
        ttk.Label(parent, text=label).pack(anchor="w")
        entry = ttk.Entry(parent, textvariable=variable)
        entry.pack(fill="x", pady=(0, 6))
        return entry

    def _build_check_tab(self):
        left = ttk.Frame(self.tab_check)
        left.pack(side="left", fill="y", padx=(0, 10))

        right = ttk.Frame(self.tab_check)
        right.pack(side="left", fill="both", expand=True)

        conn_frame = ttk.LabelFrame(left, text="서버/통신 설정", padding=10)
        conn_frame.pack(fill="x", pady=5)

        self._add_labeled_entry(conn_frame, "서버 IP", self.var_server_ip)
        self._add_labeled_entry(conn_frame, "허용 클라이언트 IP", self.var_client_ip)
        self._add_labeled_entry(conn_frame, "포트", self.var_port)
        self._add_labeled_entry(conn_frame, "최소 저장공간 MB", self.var_min_free_mb)

        ttk.Button(
            conn_frame,
            text="설정 저장",
            command=self.save_current_config
        ).pack(fill="x", pady=4)

        ttk.Button(
            conn_frame,
            text="서버 자체 점검 다시 실행",
            command=self.run_startup_checks
        ).pack(fill="x", pady=4)

        ttk.Button(
            conn_frame,
            text="클라이언트 ping 확인",
            command=self.run_client_ping_only
        ).pack(fill="x", pady=4)

        check_frame = ttk.LabelFrame(right, text="서버 점검 결과", padding=8)
        check_frame.pack(fill="both", expand=True)

        self.check_text = ScrolledText(check_frame, height=25)
        self.check_text.pack(fill="both", expand=True)

    def _build_command_tab(self):
        left = ttk.Frame(self.tab_command)
        left.pack(side="left", fill="y", padx=(0, 10))

        right = ttk.Frame(self.tab_command)
        right.pack(side="left", fill="both", expand=True)

        robot_frame = ttk.LabelFrame(left, text="로봇/명령 기본값", padding=10)
        robot_frame.pack(fill="x", pady=5)

        ttk.Label(robot_frame, text="대상 로봇").pack(anchor="w")
        robot_combo = ttk.Combobox(
            robot_frame,
            textvariable=self.var_robot,
            values=["tb3_1", "tb3_2"],
            state="readonly"
        )
        robot_combo.pack(fill="x", pady=(0, 6))

        self._add_labeled_entry(robot_frame, "ROS2 topic", self.var_topic)
        self._add_labeled_entry(robot_frame, "직선속도 lx", self.var_lx)
        self._add_labeled_entry(robot_frame, "회전속도 az", self.var_az)
        self._add_labeled_entry(robot_frame, "회전 기본값 turn_az", self.var_turn_az)
        self._add_labeled_entry(robot_frame, "수행시간 dur", self.var_dur)
        self._add_labeled_entry(robot_frame, "발행주기 hz", self.var_hz)
        self._add_labeled_entry(robot_frame, "timeout", self.var_timeout)

        btn_frame = ttk.LabelFrame(left, text="HMI 명령 버튼", padding=10)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="전진", command=self.create_forward).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="후진", command=self.create_backward).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="좌회전", command=self.create_turn_left).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="우회전", command=self.create_turn_right).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="사용자 지정 move_vel", command=self.create_custom_move).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="정지 stop", command=self.create_stop).pack(fill="x", pady=2)

        preview_frame = ttk.LabelFrame(right, text="json_command v0.3 미리보기", padding=8)
        preview_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.json_text = ScrolledText(preview_frame, height=22)
        self.json_text.pack(fill="both", expand=True)

        log_frame = ttk.LabelFrame(right, text="작업 로그", padding=8)
        log_frame.pack(fill="both", expand=False)

        self.log_text = ScrolledText(log_frame, height=10)
        self.log_text.pack(fill="both", expand=True)

    def _build_camera_tab(self):
        top = ttk.Frame(self.tab_camera)
        top.pack(fill="x", pady=(0, 8))

        ttk.Label(top, text="카메라 index").pack(side="left")
        ttk.Entry(top, textvariable=self.var_camera_index, width=8).pack(side="left", padx=5)

        ttk.Button(top, text="카메라 자동 검색", command=self.auto_search_camera).pack(side="left", padx=5)
        ttk.Button(top, text="웹캠 시작", command=self.start_camera).pack(side="left", padx=5)
        ttk.Button(top, text="웹캠 정지", command=self.stop_camera).pack(side="left", padx=5)

        self.camera_status = tk.StringVar(value="웹캠 대기 중")
        ttk.Label(top, textvariable=self.camera_status, font=("Arial", 10, "bold")).pack(side="left", padx=10)

        middle = ttk.Frame(self.tab_camera)
        middle.pack(fill="both", expand=True)

        self.camera_label = ttk.Label(
            middle,
            text="웹캠 화면이 여기에 표시됩니다.",
            anchor="center"
        )
        self.camera_label.pack(fill="both", expand=True)

        bottom = ttk.LabelFrame(self.tab_camera, text="카메라 점검 로그", padding=8)
        bottom.pack(fill="both", expand=False, pady=(8, 0))

        self.camera_log_text = ScrolledText(bottom, height=8)
        self.camera_log_text.pack(fill="both", expand=True)

    # --------------------------------------------------------
    # 출력 함수
    # --------------------------------------------------------

    def append_check(self, text):
        self.check_text.insert("end", text + "\n")
        self.check_text.see("end")

    def append_log(self, text):
        self.log_text.insert("end", f"[{now_ts()}] {text}\n")
        self.log_text.see("end")

    def append_camera_log(self, text):
        self.camera_log_text.insert("end", f"[{now_ts()}] {text}\n")
        self.camera_log_text.see("end")

    def show_json(self, data):
        self.json_text.delete("1.0", "end")
        self.json_text.insert("end", json.dumps(data, ensure_ascii=False, indent=2))

    # --------------------------------------------------------
    # 설정/점검
    # --------------------------------------------------------

    def save_current_config(self):
        config = {
            "server_ip": self.var_server_ip.get().strip(),
            "allowed_client_ip": self.var_client_ip.get().strip(),
            "port": to_int(self.var_port.get(), DEFAULT_CONFIG["port"]),

            "default_robot": self.var_robot.get().strip(),
            "default_topic": self.var_topic.get().strip(),

            "default_lx": to_float(self.var_lx.get(), DEFAULT_CONFIG["default_lx"]),
            "default_az": to_float(self.var_az.get(), DEFAULT_CONFIG["default_az"]),
            "default_turn_az": to_float(self.var_turn_az.get(), DEFAULT_CONFIG["default_turn_az"]),
            "default_dur": to_float(self.var_dur.get(), DEFAULT_CONFIG["default_dur"]),
            "default_hz": to_int(self.var_hz.get(), DEFAULT_CONFIG["default_hz"]),
            "default_timeout": to_float(self.var_timeout.get(), DEFAULT_CONFIG["default_timeout"]),

            "min_free_mb": to_int(self.var_min_free_mb.get(), DEFAULT_CONFIG["min_free_mb"]),
            "camera_index": to_int(self.var_camera_index.get(), DEFAULT_CONFIG["camera_index"])
        }

        save_config(config)
        self.config_data = config
        self.append_log(f"설정 저장 완료: {CONFIG_FILE}")
        messagebox.showinfo("설정 저장", "설정을 저장했습니다.")

    def run_startup_checks(self):
        self.check_text.delete("1.0", "end")

        self.append_check("====================================")
        self.append_check(" SERVER v0.3 STARTUP CHECK")
        self.append_check("====================================")

        ensure_log_dirs()

        self.append_check(f"[INFO] config file: {CONFIG_FILE}")
        self.append_check(f"[INFO] log root: {LOG_ROOT}")

        local_ips = get_local_ip_candidates()

        if local_ips:
            self.append_check(f"[INFO] local IP candidates: {', '.join(local_ips)}")
        else:
            self.append_check("[WARN] local IP 후보를 찾지 못했습니다.")

        min_free_mb = to_int(self.var_min_free_mb.get(), DEFAULT_CONFIG["min_free_mb"])
        ok_disk, msg_disk = check_disk_space(".", min_free_mb)
        self.append_check(("[OK] " if ok_disk else "[WARN] ") + msg_disk)

        ok_write, msg_write = check_json_write()
        self.append_check(("[OK] " if ok_write else "[ERROR] ") + msg_write)

        server_ip = self.var_server_ip.get().strip()
        port = to_int(self.var_port.get(), DEFAULT_CONFIG["port"])

        ok_port, msg_port = check_port_available(server_ip, port)
        self.append_check(("[OK] " if ok_port else "[WARN] ") + f"server bind check: {msg_port}")

        client_ip = self.var_client_ip.get().strip()
        ok_ping, msg_ping = check_client_ping(client_ip)
        self.append_check(("[OK] " if ok_ping else "[WARN] ") + msg_ping)

        status = {
            "v": 3,
            "mt": "server_startup_check",
            "ts": now_ts(),
            "server_ip": server_ip,
            "allowed_client_ip": client_ip,
            "port": port,
            "disk_ok": ok_disk,
            "json_write_ok": ok_write,
            "bind_ok": ok_port,
            "client_ping_ok": ok_ping,
            "local_ips": local_ips
        }

        try:
            save_json_log("system", "startup_check", status)
            self.append_check("[OK] startup_check 로그 저장 완료")
        except Exception as e:
            self.append_check(f"[ERROR] startup_check 로그 저장 실패: {e}")

        if ok_disk and ok_write:
            self.var_status.set("서버 HMI 준비 완료: JSON 명령 생성 가능")
        else:
            self.var_status.set("서버 HMI 경고: 저장공간 또는 JSON 저장 확인 필요")

        self.append_check("====================================")

    def run_client_ping_only(self):
        client_ip = self.var_client_ip.get().strip()
        ok_ping, msg_ping = check_client_ping(client_ip)
        self.append_check(("[OK] " if ok_ping else "[WARN] ") + msg_ping)

    # --------------------------------------------------------
    # 카메라
    # --------------------------------------------------------

    def auto_search_camera(self):
        self.append_camera_log("카메라 자동 검색 시작")

        results = find_available_cameras(max_index=6)

        if not results:
            self.camera_status.set("카메라 장치 없음")
            self.append_camera_log("검색 결과: 카메라 장치 없음")
            return

        found = None

        for item in results:
            prefix = "[OK]" if item["ok"] else "[WARN]"
            self.append_camera_log(f"{prefix} {item['msg']}")

            if item["ok"] and found is None:
                found = item

        data = {
            "v": 3,
            "mt": "camera_search",
            "ts": now_ts(),
            "results": results
        }

        try:
            save_json_log("system", "camera_search", data)
        except Exception as e:
            self.append_camera_log(f"카메라 검색 로그 저장 실패: {e}")

        if found is not None:
            self.var_camera_index.set(str(found["index"]))
            self.camera_status.set(f"/dev/video{found['index']} 사용 가능")
            self.append_camera_log(f"자동 선택: /dev/video{found['index']}")
        else:
            self.camera_status.set("사용 가능한 카메라 없음")

    def start_camera(self):
        try:
            import cv2
        except Exception as e:
            self.camera_status.set("OpenCV import 실패")
            self.append_camera_log(f"OpenCV import 실패: {e}")
            return

        if self.camera_running:
            self.append_camera_log("이미 웹캠이 실행 중입니다.")
            return

        index = to_int(self.var_camera_index.get(), 0)

        self.camera_cap = cv2.VideoCapture(index, cv2.CAP_V4L2)

        if not self.camera_cap.isOpened():
            self.camera_status.set(f"/dev/video{index} 열기 실패")
            self.append_camera_log(f"/dev/video{index} 열기 실패")
            self.camera_cap.release()
            self.camera_cap = None
            return

        self.camera_running = True
        self.camera_status.set(f"/dev/video{index} 웹캠 실행 중")
        self.append_camera_log(f"/dev/video{index} 웹캠 시작")
        self.update_camera_frame()

    def update_camera_frame(self):
        if not self.camera_running or self.camera_cap is None:
            return

        try:
            import cv2
            from PIL import Image, ImageTk

            ok, frame = self.camera_cap.read()

            if not ok or frame is None:
                self.camera_status.set("프레임 읽기 실패")
                self.append_camera_log("프레임 읽기 실패")
                self.after(500, self.update_camera_frame)
                return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            max_w = max(self.camera_label.winfo_width(), 640)
            max_h = max(self.camera_label.winfo_height(), 420)

            h, w = frame.shape[:2]
            scale = min(max_w / w, max_h / h, 1.0)

            new_w = int(w * scale)
            new_h = int(h * scale)

            frame = cv2.resize(frame, (new_w, new_h))

            image = Image.fromarray(frame)
            self.camera_image_tk = ImageTk.PhotoImage(image=image)

            self.camera_label.configure(image=self.camera_image_tk, text="")

        except Exception as e:
            self.camera_status.set("웹캠 표시 오류")
            self.append_camera_log(f"웹캠 표시 오류: {e}")

        self.after(30, self.update_camera_frame)

    def stop_camera(self):
        self.camera_running = False

        if self.camera_cap is not None:
            self.camera_cap.release()
            self.camera_cap = None

        self.camera_label.configure(image="", text="웹캠 화면이 여기에 표시됩니다.")
        self.camera_status.set("웹캠 정지")
        self.append_camera_log("웹캠 정지")

    # --------------------------------------------------------
    # 명령 생성
    # --------------------------------------------------------

    def get_common_values(self):
        robot = self.var_robot.get().strip()
        topic = self.var_topic.get().strip()
        lx = to_float(self.var_lx.get(), DEFAULT_CONFIG["default_lx"])
        az = to_float(self.var_az.get(), DEFAULT_CONFIG["default_az"])
        turn_az = to_float(self.var_turn_az.get(), DEFAULT_CONFIG["default_turn_az"])
        dur = to_float(self.var_dur.get(), DEFAULT_CONFIG["default_dur"])
        hz = to_int(self.var_hz.get(), DEFAULT_CONFIG["default_hz"])
        timeout = to_float(self.var_timeout.get(), DEFAULT_CONFIG["default_timeout"])

        return robot, topic, lx, az, turn_az, dur, hz, timeout

    def save_and_preview_command(self, cmd):
        valid, msg = validate_command_v03(cmd)

        self.latest_command = cmd
        self.show_json(cmd)

        if valid:
            self.append_log(f"json_command 생성 OK: {cmd['id']} / op={cmd['op']}")
        else:
            self.append_log(f"json_command 검증 실패: {msg}")

        try:
            history_path, latest_path = save_json_log(
                "commands",
                "json_command_preview",
                cmd
            )
            self.append_log(f"명령 로그 저장: {history_path}")
            self.append_log(f"최신 명령 저장: {latest_path}")
        except Exception as e:
            self.append_log(f"명령 로그 저장 실패: {e}")

        self.command_seq += 1

    def create_forward(self):
        robot, topic, lx, az, turn_az, dur, hz, timeout = self.get_common_values()

        cmd = make_move_vel_command(
            self.command_seq,
            robot,
            topic,
            abs(lx),
            0.0,
            dur,
            hz,
            True,
            timeout
        )

        self.save_and_preview_command(cmd)

    def create_backward(self):
        robot, topic, lx, az, turn_az, dur, hz, timeout = self.get_common_values()

        cmd = make_move_vel_command(
            self.command_seq,
            robot,
            topic,
            -abs(lx),
            0.0,
            dur,
            hz,
            True,
            timeout
        )

        self.save_and_preview_command(cmd)

    def create_turn_left(self):
        robot, topic, lx, az, turn_az, dur, hz, timeout = self.get_common_values()

        cmd = make_move_vel_command(
            self.command_seq,
            robot,
            topic,
            0.0,
            abs(turn_az),
            dur,
            hz,
            True,
            timeout
        )

        self.save_and_preview_command(cmd)

    def create_turn_right(self):
        robot, topic, lx, az, turn_az, dur, hz, timeout = self.get_common_values()

        cmd = make_move_vel_command(
            self.command_seq,
            robot,
            topic,
            0.0,
            -abs(turn_az),
            dur,
            hz,
            True,
            timeout
        )

        self.save_and_preview_command(cmd)

    def create_custom_move(self):
        robot, topic, lx, az, turn_az, dur, hz, timeout = self.get_common_values()

        cmd = make_move_vel_command(
            self.command_seq,
            robot,
            topic,
            lx,
            az,
            dur,
            hz,
            True,
            timeout
        )

        self.save_and_preview_command(cmd)

    def create_stop(self):
        robot, topic, lx, az, turn_az, dur, hz, timeout = self.get_common_values()

        cmd = make_stop_command(
            self.command_seq,
            robot,
            topic,
            1.0,
            hz,
            2.0
        )

        self.save_and_preview_command(cmd)

    def on_close(self):
        self.stop_camera()
        self.destroy()


def main():
    app = ServerHMI()
    app.mainloop()


if __name__ == "__main__":
    main()
