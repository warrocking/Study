import cv2
import numpy as np
import json
import time
import math
from pathlib import Path
from datetime import datetime
from collections import deque


# ============================================================
# 파일/창 이름
# ============================================================

CONFIG_FILE = Path("opencv_safety_config.json")
EVENT_DIR = Path("opencv_safety_events")
SHOT_DIR = Path("opencv_safety_screenshots")

MAIN_WIN = "OpenCV Safety Calibration v0.1"
CTRL_WIN = "Safety Calibration Controls"


# ============================================================
# 기본 설정값
# ============================================================

DEFAULT_CONFIG = {
    "camera_index": 0,
    "width": 640,
    "height": 480,

    # ROI. 0이면 전체 화면 사용
    "roi_x": 0,
    "roi_y": 0,
    "roi_w": 0,
    "roi_h": 0,

    # 검은색 TurtleBot HSV 범위
    "black_h_low": 0,
    "black_h_high": 179,
    "black_s_low": 0,
    "black_s_high": 255,
    "black_v_low": 0,
    "black_v_high": 70,

    # TurtleBot contour 조건
    "robot_min_area": 800,
    "robot_max_area": 30000,
    "robot_aspect_min_x100": 50,     # 0.50
    "robot_aspect_max_x100": 200,    # 2.00
    "robot_expand_px": 25,
    "track_lost_x10": 20,            # 2.0초

    # Canny
    "canny_auto": 1,
    "canny_sigma_x100": 33,          # 0.33
    "canny_low": 80,
    "canny_high": 160,
    "edge_warn_x1000": 40,           # 0.040
    "edge_pause_x1000": 100,         # 0.100

    # MOG2 / Motion
    "mog2_history": 300,
    "mog2_var_threshold": 25,
    "morph_kernel": 5,
    "motion_min_area": 800,
    "motion_warn_x1000": 50,         # 0.050
    "motion_pause_x1000": 150,       # 0.150

    # TurtleBot stuck 판단
    "move_min_px": 10,
    "stuck_time_x10": 40,            # 4.0초

    # HOG 사람 검출
    "hog_enable": 0,
    "hog_every": 10,
    "person_pause_frames": 3,

    # 카메라 상태
    "light_dark": 40,
    "light_bright": 230,
    "blur_min": 40,
    "fps_min": 10,
    "freeze_sec_x10": 20             # 2.0초
}


TRACKBARS = [
    ("black_h_low", 179),
    ("black_h_high", 179),
    ("black_s_low", 255),
    ("black_s_high", 255),
    ("black_v_low", 255),
    ("black_v_high", 255),

    ("robot_min_area", 50000),
    ("robot_max_area", 100000),
    ("robot_aspect_min_x100", 500),
    ("robot_aspect_max_x100", 500),
    ("robot_expand_px", 150),
    ("track_lost_x10", 100),

    ("canny_auto", 1),
    ("canny_sigma_x100", 100),
    ("canny_low", 255),
    ("canny_high", 255),
    ("edge_warn_x1000", 500),
    ("edge_pause_x1000", 500),

    ("morph_kernel", 31),
    ("motion_min_area", 50000),
    ("motion_warn_x1000", 500),
    ("motion_pause_x1000", 500),

    ("move_min_px", 300),
    ("stuck_time_x10", 200),

    ("hog_enable", 1),
    ("hog_every", 60),
    ("person_pause_frames", 30),

    ("light_dark", 255),
    ("light_bright", 255),
    ("blur_min", 1000),
    ("fps_min", 60),
    ("freeze_sec_x10", 100)
]


# ============================================================
# 기본 유틸
# ============================================================

def now_ts():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_name():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def load_config():
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            loaded = json.load(f)

        cfg = dict(DEFAULT_CONFIG)
        cfg.update(loaded)
        return cfg

    except Exception:
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def save_event(event):
    EVENT_DIR.mkdir(parents=True, exist_ok=True)

    latest_path = EVENT_DIR / "latest_opencv_event.json"
    history_path = EVENT_DIR / f"opencv_event_{now_name()}.json"

    with latest_path.open("w", encoding="utf-8") as f:
        json.dump(event, f, ensure_ascii=False, indent=2)

    with history_path.open("w", encoding="utf-8") as f:
        json.dump(event, f, ensure_ascii=False, indent=2)


def clamp(value, low, high):
    return max(low, min(high, value))


def empty_callback(_):
    pass


def put_text(img, text, x, y, color=(255, 255, 255), scale=0.55, thickness=1):
    cv2.putText(
        img,
        str(text),
        (int(x), int(y)),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA
    )


def add_header(img, title):
    out = img.copy()
    cv2.rectangle(out, (0, 0), (out.shape[1], 28), (0, 0, 0), -1)
    put_text(out, title, 8, 20, (255, 255, 255), 0.55, 1)
    return out


def ensure_bgr(img):
    if img is None:
        return np.zeros((240, 320, 3), dtype=np.uint8)

    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    return img


def resize_tile(img, w=480, h=270):
    img = ensure_bgr(img)
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)


def make_grid(images, tile_w=480, tile_h=270, cols=2):
    tiles = [resize_tile(img, tile_w, tile_h) for img in images]

    while len(tiles) % cols != 0:
        tiles.append(np.zeros((tile_h, tile_w, 3), dtype=np.uint8))

    rows = []

    for i in range(0, len(tiles), cols):
        rows.append(np.hstack(tiles[i:i + cols]))

    return np.vstack(rows)


def get_odd_kernel_size(value):
    k = int(value)

    if k < 1:
        k = 1

    if k % 2 == 0:
        k += 1

    return k


def clean_mask(mask, kernel_size):
    k = get_odd_kernel_size(kernel_size)
    kernel = np.ones((k, k), np.uint8)

    blur_k = k if k >= 3 else 3
    out = cv2.medianBlur(mask, blur_k)
    out = cv2.morphologyEx(out, cv2.MORPH_OPEN, kernel)
    out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, kernel)

    return out


def auto_canny(gray, sigma):
    med = np.median(gray)
    lower = int(max(0, (1.0 - sigma) * med))
    upper = int(min(255, (1.0 + sigma) * med))

    if upper <= lower:
        upper = min(255, lower + 1)

    edged = cv2.Canny(gray, lower, upper)
    return edged, lower, upper


def create_mog2(cfg):
    return cv2.createBackgroundSubtractorMOG2(
        history=max(10, int(cfg["mog2_history"])),
        varThreshold=max(1, int(cfg["mog2_var_threshold"])),
        detectShadows=True
    )


# ============================================================
# Trackbar 제어창
# ============================================================

def create_controls(cfg):
    cv2.namedWindow(CTRL_WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(CTRL_WIN, 460, 760)

    for key, max_value in TRACKBARS:
        initial = int(cfg.get(key, DEFAULT_CONFIG[key]))
        initial = clamp(initial, 0, max_value)
        cv2.createTrackbar(key, CTRL_WIN, initial, max_value, empty_callback)


def read_controls(cfg):
    new_cfg = dict(cfg)

    for key, max_value in TRACKBARS:
        try:
            value = cv2.getTrackbarPos(key, CTRL_WIN)
        except Exception:
            value = int(new_cfg.get(key, DEFAULT_CONFIG[key]))

        if key in [
            "robot_max_area",
            "robot_aspect_max_x100",
            "canny_sigma_x100",
            "morph_kernel",
            "hog_every",
            "stuck_time_x10",
            "freeze_sec_x10"
        ]:
            value = max(value, 1)

        new_cfg[key] = int(value)

    return new_cfg


# ============================================================
# ROI
# ============================================================

def get_roi(frame, cfg):
    h, w = frame.shape[:2]

    x = int(cfg.get("roi_x", 0))
    y = int(cfg.get("roi_y", 0))
    rw = int(cfg.get("roi_w", 0))
    rh = int(cfg.get("roi_h", 0))

    if rw <= 0 or rh <= 0:
        return 0, 0, w, h

    x = clamp(x, 0, w - 1)
    y = clamp(y, 0, h - 1)
    rw = clamp(rw, 1, w - x)
    rh = clamp(rh, 1, h - y)

    return x, y, rw, rh


def select_roi(frame, cfg):
    print("[INFO] ROI 선택 창이 뜹니다. 드래그 후 Enter, 취소는 ESC 또는 C.")

    roi = cv2.selectROI(
        "Select ROI",
        frame,
        fromCenter=False,
        showCrosshair=True
    )

    cv2.destroyWindow("Select ROI")

    x, y, w, h = roi

    if w > 0 and h > 0:
        cfg["roi_x"] = int(x)
        cfg["roi_y"] = int(y)
        cfg["roi_w"] = int(w)
        cfg["roi_h"] = int(h)
        save_config(cfg)
        print(f"[INFO] ROI 저장: x={x}, y={y}, w={w}, h={h}")
    else:
        print("[WARN] ROI 선택 취소 또는 잘못된 ROI")

    return cfg


# ============================================================
# 검은색 TurtleBot 추적
# ============================================================

def detect_black_robot(roi_bgr, cfg):
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)

    lower = np.array([
        int(cfg["black_h_low"]),
        int(cfg["black_s_low"]),
        int(cfg["black_v_low"])
    ], dtype=np.uint8)

    upper = np.array([
        int(cfg["black_h_high"]),
        int(cfg["black_s_high"]),
        int(cfg["black_v_high"])
    ], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower, upper)
    mask = clean_mask(mask, int(cfg["morph_kernel"]))

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    min_area = float(cfg["robot_min_area"])
    max_area = float(cfg["robot_max_area"])
    aspect_min = float(cfg["robot_aspect_min_x100"]) / 100.0
    aspect_max = float(cfg["robot_aspect_max_x100"]) / 100.0

    candidates = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < min_area or area > max_area:
            continue

        x, y, w, h = cv2.boundingRect(cnt)

        if h <= 0:
            continue

        aspect = w / float(h)

        if aspect < aspect_min or aspect > aspect_max:
            continue

        m = cv2.moments(cnt)

        if m["m00"] == 0:
            cx = x + w // 2
            cy = y + h // 2
        else:
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])

        candidates.append({
            "contour": cnt,
            "area": area,
            "bbox": (x, y, w, h),
            "center": (cx, cy),
            "aspect": aspect
        })

    candidates.sort(key=lambda item: item["area"], reverse=True)

    robot = candidates[0] if candidates else None

    return robot, mask, candidates


# ============================================================
# Motion / Edge / Person / Camera Health
# ============================================================

def detect_motion(roi_bgr, mog2, robot_bbox, cfg):
    fg = mog2.apply(roi_bgr)

    # MOG2 shadow 값 127 제거
    _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
    fg = clean_mask(fg, int(cfg["morph_kernel"]))

    # TurtleBot 자체 움직임은 unknown motion에서 제외
    if robot_bbox is not None:
        x, y, w, h = robot_bbox
        expand = int(cfg["robot_expand_px"])

        x1 = max(0, x - expand)
        y1 = max(0, y - expand)
        x2 = min(fg.shape[1], x + w + expand)
        y2 = min(fg.shape[0], y + h + expand)

        fg[y1:y2, x1:x2] = 0

    contours, _ = cv2.findContours(
        fg,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    min_area = float(cfg["motion_min_area"])
    large_contours = []
    total_area = 0.0

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < min_area:
            continue

        large_contours.append(cnt)
        total_area += area

    ratio = cv2.countNonZero(fg) / float(fg.size)

    return fg, large_contours, total_area, ratio


def compute_edges(roi_bgr, cfg):
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    if int(cfg["canny_auto"]) == 1:
        sigma = float(cfg["canny_sigma_x100"]) / 100.0
        edges, low, high = auto_canny(gray, sigma)
    else:
        low = int(cfg["canny_low"])
        high = int(cfg["canny_high"])
        edges = cv2.Canny(gray, low, high)

    return gray, edges, low, high


def detect_people_hog(roi_bgr, hog, frame_count, cfg, last_boxes):
    if int(cfg["hog_enable"]) != 1:
        return []

    every = max(1, int(cfg["hog_every"]))

    if frame_count % every != 0:
        return last_boxes

    small = cv2.resize(roi_bgr, None, fx=0.75, fy=0.75)

    boxes, weights = hog.detectMultiScale(
        small,
        winStride=(8, 8),
        padding=(8, 8),
        scale=1.05
    )

    scale_back = 1.0 / 0.75
    out_boxes = []

    for (x, y, w, h) in boxes:
        out_boxes.append((
            int(x * scale_back),
            int(y * scale_back),
            int(w * scale_back),
            int(h * scale_back)
        ))

    return out_boxes


def camera_health(roi_bgr, gray, prev_gray, last_change_time, cfg):
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    v_mean = float(np.mean(hsv[:, :, 2]))

    blur_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    frozen = False
    now = time.time()

    if prev_gray is not None:
        diff = cv2.absdiff(gray, prev_gray)
        diff_mean = float(np.mean(diff))

        # 완전히 고정된 이미지인지 확인.
        # 일반 웹캠은 정지 장면에서도 미세 노이즈가 있으므로 diff_mean이 0에 가깝게 유지되는 경우를 freeze 후보로 본다.
        if diff_mean > 0.4:
            last_change_time = now

        freeze_sec = float(cfg["freeze_sec_x10"]) / 10.0

        if now - last_change_time >= freeze_sec:
            frozen = True

    return {
        "v_mean": v_mean,
        "blur_var": blur_var,
        "frozen": frozen,
        "last_change_time": last_change_time
    }


# ============================================================
# 이벤트 판단
# ============================================================

def severity_rank(level):
    ranks = {
        "NORMAL": 0,
        "INFO": 1,
        "WARNING": 2,
        "PAUSE": 3,
        "EMERGENCY": 4
    }
    return ranks.get(level, 0)


def max_severity(a, b):
    return a if severity_rank(a) >= severity_rank(b) else b


def decide_event(
    cfg,
    command_running,
    robot_found,
    robot_center,
    robot_distance,
    robot_history_span,
    robot_lost_sec,
    motion_ratio,
    edge_ratio,
    person_count,
    fps,
    health
):
    level = "NORMAL"
    reasons = []

    # ---------------- 카메라 상태 ----------------

    if fps < float(cfg["fps_min"]):
        level = max_severity(level, "WARNING")
        reasons.append("LOW_FPS")

    if health["v_mean"] < float(cfg["light_dark"]):
        level = max_severity(level, "WARNING")
        reasons.append("LIGHT_TOO_DARK")

    if health["v_mean"] > float(cfg["light_bright"]):
        level = max_severity(level, "WARNING")
        reasons.append("LIGHT_TOO_BRIGHT")

    if health["blur_var"] < float(cfg["blur_min"]):
        level = max_severity(level, "WARNING")
        reasons.append("CAMERA_BLUR")

    if health["frozen"]:
        level = max_severity(level, "PAUSE")
        reasons.append("FRAME_FROZEN")

    # ---------------- 로봇 추적 ----------------

    track_lost_sec = float(cfg["track_lost_x10"]) / 10.0

    # 명령 중일 때 로봇을 잃어버리면 위험.
    # 명령이 없을 때는 캘리브레이션 중일 수 있으므로 PAUSE로 보지 않음.
    if command_running and robot_lost_sec >= track_lost_sec:
        level = max_severity(level, "PAUSE")
        reasons.append("ROBOT_LOST")

    # stuck은 충분한 시간 창이 쌓인 뒤에만 판단
    if command_running and robot_found:
        stuck_time_sec = float(cfg["stuck_time_x10"]) / 10.0
        move_min_px = float(cfg["move_min_px"])

        if (
            robot_distance is not None
            and robot_history_span is not None
            and robot_history_span >= stuck_time_sec
            and robot_distance < move_min_px
        ):
            level = max_severity(level, "PAUSE")
            reasons.append("ROBOT_STUCK")

    # ---------------- 사람 ----------------

    if person_count > 0:
        level = max_severity(level, "PAUSE")
        reasons.append("PERSON_DETECTED")

    # ---------------- 장면 변화 ----------------

    motion_warn = float(cfg["motion_warn_x1000"]) / 1000.0
    motion_pause = float(cfg["motion_pause_x1000"]) / 1000.0
    edge_warn = float(cfg["edge_warn_x1000"]) / 1000.0
    edge_pause = float(cfg["edge_pause_x1000"]) / 1000.0

    if motion_ratio >= motion_pause:
        level = max_severity(level, "PAUSE")
        reasons.append("LARGE_MOTION_CHANGE")
    elif motion_ratio >= motion_warn:
        level = max_severity(level, "WARNING")
        reasons.append("MOTION_CHANGE")

    if edge_ratio >= edge_pause:
        level = max_severity(level, "PAUSE")
        reasons.append("LARGE_EDGE_CHANGE")
    elif edge_ratio >= edge_warn:
        level = max_severity(level, "WARNING")
        reasons.append("EDGE_CHANGE")

    if not reasons:
        reasons.append("NONE")

    main_event = reasons[0] if reasons[0] != "NONE" else "NORMAL"

    return level, main_event, reasons


# ============================================================
# 화면 구성
# ============================================================

def draw_status_panel(frame_shape, event, command_running):
    h, w = frame_shape[:2]
    panel = np.zeros((h, w, 3), dtype=np.uint8)

    level = event["lv"]
    color = (0, 255, 0)

    if level == "WARNING":
        color = (0, 255, 255)
    elif level == "PAUSE":
        color = (0, 128, 255)
    elif level == "EMERGENCY":
        color = (0, 0, 255)

    panel = add_header(panel, "Safety Summary")

    y = 55
    put_text(panel, f"event_level: {level}", 15, y, color, 0.75, 2)
    y += 32

    put_text(panel, f"main_event: {event['event']}", 15, y, (255, 255, 255), 0.6, 1)
    y += 26

    put_text(panel, f"command_running: {command_running}", 15, y, (255, 255, 255), 0.6, 1)
    y += 26

    data = event["data"]

    lines = [
        f"robot_found: {data['robot_found']}",
        f"robot_center: {data['robot_center']}",
        f"robot_distance_px: {data['robot_distance_px']}",
        f"robot_history_span: {data['robot_history_span_sec']}",
        f"robot_lost_sec: {data['robot_lost_sec']:.1f}",
        f"motion_ratio: {data['motion_ratio']:.3f}",
        f"edge_ratio: {data['edge_ratio']:.3f}",
        f"person_count: {data['person_count']}",
        f"fps: {data['fps']:.1f}",
        f"brightness_v: {data['brightness_v']:.1f}",
        f"blur_var: {data['blur_var']:.1f}",
        f"frozen: {data['frame_frozen']}"
    ]

    for line in lines:
        put_text(panel, line, 15, y, (200, 200, 200), 0.52, 1)
        y += 23

    y += 10
    put_text(panel, "Keys:", 15, y, (255, 255, 0), 0.55, 1)
    y += 24

    key_lines = [
        "q/ESC quit",
        "s save config",
        "r select ROI",
        "f reset reference",
        "m toggle RUNNING",
        "i set IDLE",
        "g reset MOG2",
        "h toggle HOG",
        "p pause",
        "c screenshot"
    ]

    for line in key_lines:
        put_text(panel, line, 15, y, (180, 180, 180), 0.48, 1)
        y += 21

    return panel


# ============================================================
# 메인
# ============================================================

def main():
    cfg = load_config()

    cap = cv2.VideoCapture(int(cfg["camera_index"]), cv2.CAP_V4L2)

    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(int(cfg["camera_index"]))

    if not cap.isOpened():
        print(f"[ERROR] 카메라 열기 실패: index {cfg['camera_index']}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(cfg["width"]))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(cfg["height"]))

    cv2.namedWindow(MAIN_WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(MAIN_WIN, 1280, 780)

    create_controls(cfg)

    mog2 = create_mog2(cfg)

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    last_hog_boxes = []

    ref_edges = None
    ref_gray = None

    prev_gray_health = None
    last_frame_change_time = time.time()

    centroid_history = deque()
    last_robot_seen_time = time.time()

    command_running = False
    paused = False
    frame_count = 0

    last_time = time.time()
    fps = 0.0
    fps_smooth = None

    last_event_signature = None
    last_event_save_time = 0.0
    last_grid = None
    last_frame = None

    print("====================================")
    print("OpenCV Safety Calibration v0.1")
    print("q/ESC: 종료")
    print("s: 설정 저장")
    print("r: ROI 선택")
    print("f: 기준 프레임 reset")
    print("m: command_running 토글")
    print("i: IDLE 설정")
    print("g: MOG2 reset")
    print("h: HOG on/off")
    print("p: 일시정지/재개")
    print("c: screenshot 저장")
    print("====================================")

    while True:
        cfg = read_controls(cfg)

        if not paused:
            ok, frame = cap.read()

            if not ok or frame is None:
                print("[WARN] 프레임 읽기 실패")
                time.sleep(0.05)
                continue

            frame_count += 1
            last_frame = frame.copy()

            now = time.time()
            dt = now - last_time
            last_time = now

            if dt > 0:
                current_fps = 1.0 / dt

                if fps_smooth is None:
                    fps_smooth = current_fps
                else:
                    fps_smooth = 0.9 * fps_smooth + 0.1 * current_fps

                fps = fps_smooth

            rx, ry, rw, rh = get_roi(frame, cfg)
            roi = frame[ry:ry + rh, rx:rx + rw].copy()

            if roi.size == 0:
                roi = frame.copy()
                rx, ry, rw, rh = 0, 0, frame.shape[1], frame.shape[0]

            # --------------------------------------------------
            # 1. 검은색 TurtleBot 추적
            # --------------------------------------------------

            robot, black_mask, robot_candidates = detect_black_robot(roi, cfg)

            robot_found = robot is not None
            robot_center_global = None
            robot_bbox = None

            if robot_found:
                bx, by, bw, bh = robot["bbox"]
                cx, cy = robot["center"]

                robot_bbox = (bx, by, bw, bh)
                robot_center_global = (rx + cx, ry + cy)
                last_robot_seen_time = time.time()

                centroid_history.append((
                    time.time(),
                    robot_center_global[0],
                    robot_center_global[1]
                ))

            robot_lost_sec = time.time() - last_robot_seen_time

            stuck_time_sec = float(cfg["stuck_time_x10"]) / 10.0
            oldest_allowed = time.time() - stuck_time_sec

            while centroid_history and centroid_history[0][0] < oldest_allowed:
                centroid_history.popleft()

            robot_distance = None
            robot_history_span = None

            if len(centroid_history) >= 2:
                t0, x0, y0 = centroid_history[0]
                t1, x1, y1 = centroid_history[-1]

                robot_history_span = t1 - t0
                robot_distance = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

            # --------------------------------------------------
            # 2. MOG2 Motion
            # --------------------------------------------------

            fg_mask, motion_contours, motion_area, motion_ratio = detect_motion(
                roi,
                mog2,
                robot_bbox,
                cfg
            )

            # --------------------------------------------------
            # 3. Canny / Edge Difference
            # --------------------------------------------------

            gray, edges, canny_low_used, canny_high_used = compute_edges(roi, cfg)

            if ref_edges is None or ref_gray is None:
                ref_gray = gray.copy()
                ref_edges = edges.copy()

            edge_diff = cv2.absdiff(edges, ref_edges)
            edge_ratio = cv2.countNonZero(edge_diff) / float(edge_diff.size)

            # --------------------------------------------------
            # 4. HOG 사람 검출
            # --------------------------------------------------

            last_hog_boxes = detect_people_hog(
                roi,
                hog,
                frame_count,
                cfg,
                last_hog_boxes
            )

            person_count = len(last_hog_boxes)

            # --------------------------------------------------
            # 5. 카메라 상태
            # --------------------------------------------------

            health = camera_health(
                roi,
                gray,
                prev_gray_health,
                last_frame_change_time,
                cfg
            )

            last_frame_change_time = health["last_change_time"]
            prev_gray_health = gray.copy()

            # --------------------------------------------------
            # 6. 이벤트 판단
            # --------------------------------------------------

            level, main_event, reasons = decide_event(
                cfg=cfg,
                command_running=command_running,
                robot_found=robot_found,
                robot_center=robot_center_global,
                robot_distance=robot_distance,
                robot_history_span=robot_history_span,
                robot_lost_sec=robot_lost_sec,
                motion_ratio=motion_ratio,
                edge_ratio=edge_ratio,
                person_count=person_count,
                fps=fps,
                health=health
            )

            event = {
                "v": 3,
                "mt": "event",
                "ts": now_ts(),
                "src": f"opencv_camera_{cfg['camera_index']}",
                "lv": level,
                "event": main_event,
                "reasons": reasons,
                "data": {
                    "command_running": command_running,
                    "robot_found": robot_found,
                    "robot_center": list(robot_center_global) if robot_center_global else None,
                    "robot_distance_px": round(robot_distance, 2) if robot_distance is not None else None,
                    "robot_history_span_sec": round(robot_history_span, 2) if robot_history_span is not None else None,
                    "robot_lost_sec": round(robot_lost_sec, 2),
                    "motion_ratio": round(motion_ratio, 4),
                    "edge_ratio": round(edge_ratio, 4),
                    "person_count": person_count,
                    "fps": round(float(fps), 2),
                    "brightness_v": round(float(health["v_mean"]), 2),
                    "blur_var": round(float(health["blur_var"]), 2),
                    "frame_frozen": bool(health["frozen"]),
                    "canny_low_used": int(canny_low_used),
                    "canny_high_used": int(canny_high_used),
                    "roi": {
                        "x": rx,
                        "y": ry,
                        "w": rw,
                        "h": rh
                    }
                }
            }

            event_signature = f"{level}:{main_event}:{','.join(reasons)}"
            now_save = time.time()

            if event_signature != last_event_signature or now_save - last_event_save_time > 2.0:
                try:
                    save_event(event)
                    last_event_signature = event_signature
                    last_event_save_time = now_save
                except Exception as e:
                    print("[WARN] event 저장 실패:", e)

            # --------------------------------------------------
            # 7. 화면 구성
            # --------------------------------------------------

            original_view = frame.copy()
            cv2.rectangle(
                original_view,
                (rx, ry),
                (rx + rw, ry + rh),
                (255, 255, 0),
                2
            )

            if robot_found:
                bx, by, bw, bh = robot["bbox"]
                cx, cy = robot["center"]

                cv2.rectangle(
                    original_view,
                    (rx + bx, ry + by),
                    (rx + bx + bw, ry + by + bh),
                    (0, 255, 0),
                    2
                )
                cv2.circle(original_view, (rx + cx, ry + cy), 5, (0, 255, 0), -1)
                put_text(
                    original_view,
                    "black robot",
                    rx + bx,
                    max(20, ry + by - 8),
                    (0, 255, 0),
                    0.55,
                    1
                )

            for (px, py, pw, ph) in last_hog_boxes:
                cv2.rectangle(
                    original_view,
                    (rx + px, ry + py),
                    (rx + px + pw, ry + py + ph),
                    (0, 0, 255),
                    2
                )
                put_text(
                    original_view,
                    "person",
                    rx + px,
                    max(20, ry + py - 8),
                    (0, 0, 255),
                    0.55,
                    1
                )

            original_view = add_header(original_view, "Original + ROI + Robot")
            put_text(original_view, f"RUNNING={command_running}", 10, 55, (0, 255, 255), 0.6, 1)

            mask_view = cv2.cvtColor(black_mask, cv2.COLOR_GRAY2BGR)
            mask_view = add_header(mask_view, "Black Robot Mask")
            put_text(mask_view, f"candidates={len(robot_candidates)}", 10, 55, (0, 255, 255), 0.55, 1)
            put_text(mask_view, f"V high={cfg['black_v_high']}", 10, 80, (0, 255, 255), 0.55, 1)

            motion_view = roi.copy()

            for cnt in motion_contours:
                x, y, w, h = cv2.boundingRect(cnt)
                area = cv2.contourArea(cnt)
                cv2.rectangle(motion_view, (x, y), (x + w, y + h), (0, 255, 255), 2)
                put_text(motion_view, int(area), x, max(20, y - 5), (0, 255, 255), 0.5, 1)

            motion_view = add_header(motion_view, "MOG2 Unknown Motion")
            put_text(motion_view, f"motion_ratio={motion_ratio:.3f}", 10, 55, (0, 255, 255), 0.55, 1)
            put_text(motion_view, f"objects={len(motion_contours)}", 10, 80, (0, 255, 255), 0.55, 1)

            edge_view = cv2.cvtColor(edge_diff, cv2.COLOR_GRAY2BGR)
            edge_view = add_header(edge_view, "Canny Edge Difference")
            put_text(edge_view, f"edge_ratio={edge_ratio:.3f}", 10, 55, (0, 255, 255), 0.55, 1)
            put_text(edge_view, f"low/high={canny_low_used}/{canny_high_used}", 10, 80, (0, 255, 255), 0.55, 1)

            summary_view = draw_status_panel(roi.shape, event, command_running)

            grid = make_grid(
                [
                    original_view,
                    mask_view,
                    motion_view,
                    edge_view,
                    summary_view
                ],
                tile_w=480,
                tile_h=270,
                cols=2
            )

            last_grid = grid.copy()

        else:
            grid = last_grid

        if grid is not None:
            cv2.imshow(MAIN_WIN, grid)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            break

        if key == ord("p"):
            paused = not paused
            print("[INFO] paused =", paused)

        if key == ord("s"):
            cfg = read_controls(cfg)
            save_config(cfg)
            print(f"[INFO] config 저장 완료: {CONFIG_FILE}")

        if key == ord("r"):
            if last_frame is not None:
                cfg = select_roi(last_frame, cfg)

        if key == ord("f"):
            if last_frame is not None:
                rx, ry, rw, rh = get_roi(last_frame, cfg)
                roi = last_frame[ry:ry + rh, rx:rx + rw].copy()

                if roi.size == 0:
                    roi = last_frame.copy()

                gray, edges, low, high = compute_edges(roi, cfg)
                ref_gray = gray.copy()
                ref_edges = edges.copy()
                centroid_history.clear()

                print("[INFO] 기준 프레임/edge reset 완료")

        if key == ord("m"):
            command_running = not command_running
            centroid_history.clear()
            print("[INFO] command_running =", command_running)

        if key == ord("i"):
            command_running = False
            centroid_history.clear()
            print("[INFO] command_running = False")

        if key == ord("g"):
            mog2 = create_mog2(cfg)
            print("[INFO] MOG2 배경 모델 reset 완료")

        if key == ord("h"):
            current = int(cfg["hog_enable"])
            new_value = 0 if current == 1 else 1
            cv2.setTrackbarPos("hog_enable", CTRL_WIN, new_value)
            print("[INFO] HOG enable =", new_value)

        if key == ord("c"):
            if last_grid is not None:
                SHOT_DIR.mkdir(parents=True, exist_ok=True)
                path = SHOT_DIR / f"safety_calibration_{now_name()}.png"
                cv2.imwrite(str(path), last_grid)
                print(f"[INFO] screenshot 저장: {path}")

    final_cfg = read_controls(cfg)
    save_config(final_cfg)

    cap.release()
    cv2.destroyAllWindows()

    print("[INFO] 종료. 최종 config 저장 완료.")
    print(f"[INFO] config file: {CONFIG_FILE}")


if __name__ == "__main__":
    main()
