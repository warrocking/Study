import cv2
import numpy as np
import json
import time
import math
from pathlib import Path
from datetime import datetime


CONFIG_FILE = Path("opencv_safety_config.json")
WIN_ORIGINAL = "Black Robot Auto Tune - Original"
WIN_MASK = "Black Robot Auto Tune - Mask"

DEFAULT_CONFIG = {
    "camera_index": 0,
    "width": 640,
    "height": 480,

    "roi_x": 0,
    "roi_y": 0,
    "roi_w": 0,
    "roi_h": 0,

    "black_h_low": 0,
    "black_h_high": 179,
    "black_s_low": 0,
    "black_s_high": 255,
    "black_v_low": 0,
    "black_v_high": 80,

    "robot_min_area": 200,
    "robot_max_area": 50000,
    "robot_aspect_min_x100": 20,
    "robot_aspect_max_x100": 400,
    "robot_expand_px": 25,

    "robot_target_x": None,
    "robot_target_y": None,
    "robot_target_roi_x": None,
    "robot_target_roi_y": None,

    "morph_kernel": 5
}


state = {
    "last_frame": None,
    "click": None,
    "selected_bbox": None,
    "selected_center": None,
    "message": "Click TurtleBot center, then press 'a'",
    "cfg": None
}


def now_ts():
    return datetime.now().astimezone().isoformat(timespec="seconds")


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


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def get_roi(frame, cfg):
    h, w = frame.shape[:2]

    x = int(cfg.get("roi_x", 0) or 0)
    y = int(cfg.get("roi_y", 0) or 0)
    rw = int(cfg.get("roi_w", 0) or 0)
    rh = int(cfg.get("roi_h", 0) or 0)

    if rw <= 0 or rh <= 0:
        return 0, 0, w, h

    x = clamp(x, 0, w - 1)
    y = clamp(y, 0, h - 1)
    rw = clamp(rw, 1, w - x)
    rh = clamp(rh, 1, h - y)

    return x, y, rw, rh


def select_roi(frame, cfg):
    print("[INFO] ROI 선택: TurtleBot이 움직이는 바닥 영역만 드래그하세요.")
    roi = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Select ROI")

    x, y, w, h = roi

    if w > 0 and h > 0:
        cfg["roi_x"] = int(x)
        cfg["roi_y"] = int(y)
        cfg["roi_w"] = int(w)
        cfg["roi_h"] = int(h)
        save_config(cfg)
        print(f"[OK] ROI saved: x={x}, y={y}, w={w}, h={h}")
    else:
        print("[WARN] ROI 선택 취소")

    return cfg


def odd_kernel(k):
    k = int(k)

    if k < 1:
        k = 1

    if k % 2 == 0:
        k += 1

    return k


def clean_mask(mask, k=5):
    k = odd_kernel(k)
    kernel = np.ones((k, k), np.uint8)

    if k >= 3:
        mask = cv2.medianBlur(mask, k)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def make_black_mask(roi_bgr, cfg):
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
    mask = clean_mask(mask, int(cfg.get("morph_kernel", 5)))

    return mask


def find_contours(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def contour_info(cnt):
    area = cv2.contourArea(cnt)
    x, y, w, h = cv2.boundingRect(cnt)

    if h <= 0:
        aspect = 0.0
    else:
        aspect = w / float(h)

    m = cv2.moments(cnt)

    if m["m00"] == 0:
        cx = x + w // 2
        cy = y + h // 2
    else:
        cx = int(m["m10"] / m["m00"])
        cy = int(m["m01"] / m["m00"])

    return {
        "area": area,
        "bbox": (x, y, w, h),
        "center": (cx, cy),
        "aspect": aspect
    }


def choose_candidate_near_click(contours, click_local):
    if click_local is None:
        return None, None

    click_x, click_y = click_local
    best = None
    best_score = None

    for cnt in contours:
        info = contour_info(cnt)
        area = info["area"]

        if area < 20:
            continue

        x, y, w, h = info["bbox"]
        cx, cy = info["center"]

        contains = (x <= click_x <= x + w and y <= click_y <= y + h)
        dist = math.sqrt((cx - click_x) ** 2 + (cy - click_y) ** 2)

        # 클릭 지점을 포함하는 contour를 강하게 우선
        score = dist

        if contains:
            score -= 10000

        # 너무 작은 노이즈는 불리하게
        if area < 80:
            score += 500

        if best is None or score < best_score:
            best = cnt
            best_score = score

    if best is None:
        return None, None

    return best, contour_info(best)


def auto_tune_from_click(frame, cfg, click_global):
    if click_global is None:
        return cfg, None, None, "먼저 원본 화면에서 TurtleBot 중심을 클릭하세요."

    rx, ry, rw, rh = get_roi(frame, cfg)
    gx, gy = click_global

    if not (rx <= gx < rx + rw and ry <= gy < ry + rh):
        return cfg, None, None, "클릭 위치가 ROI 밖입니다. ROI 안의 TurtleBot을 클릭하세요."

    roi = frame[ry:ry + rh, rx:rx + rw].copy()
    lx = gx - rx
    ly = gy - ry

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    patch_r = 22
    x1 = clamp(lx - patch_r, 0, rw - 1)
    y1 = clamp(ly - patch_r, 0, rh - 1)
    x2 = clamp(lx + patch_r, 0, rw - 1)
    y2 = clamp(ly + patch_r, 0, rh - 1)

    patch = hsv[y1:y2 + 1, x1:x2 + 1]

    if patch.size == 0:
        return cfg, None, None, "패치 추출 실패"

    v = patch[:, :, 2].reshape(-1)
    s = patch[:, :, 1].reshape(-1)

    # 클릭 주변에서 상대적으로 어두운 픽셀만 사용
    v40 = np.percentile(v, 40)
    dark_pixels = v[v <= v40]

    if len(dark_pixels) < 20:
        dark_pixels = v[v <= np.percentile(v, 60)]

    if len(dark_pixels) < 20:
        dark_pixels = v

    v95 = float(np.percentile(dark_pixels, 95))
    v_high = int(clamp(v95 + 25, 35, 170))

    # 검은색은 Hue 의미가 약하므로 H/S는 넓게 열어둔다.
    cfg["black_h_low"] = 0
    cfg["black_h_high"] = 179
    cfg["black_s_low"] = 0
    cfg["black_s_high"] = 255
    cfg["black_v_low"] = 0
    cfg["black_v_high"] = v_high

    mask = make_black_mask(roi, cfg)
    contours = find_contours(mask)
    chosen_cnt, info = choose_candidate_near_click(contours, (lx, ly))

    if chosen_cnt is None or info is None:
        return cfg, mask, None, f"자동 후보 선택 실패. black_v_high={v_high}로는 클릭 지점 주변 contour가 약합니다."

    area = float(info["area"])
    x, y, w, h = info["bbox"]
    aspect = float(info["aspect"])
    cx, cy = info["center"]

    # 현재 클릭한 contour 기반으로 면적/비율 자동 설정
    cfg["robot_min_area"] = int(max(30, area * 0.25))
    cfg["robot_max_area"] = int(min(100000, max(area * 5.0, area + 500)))

    aspect_min = max(0.10, aspect * 0.35)
    aspect_max = min(6.00, aspect * 3.00)

    cfg["robot_aspect_min_x100"] = int(aspect_min * 100)
    cfg["robot_aspect_max_x100"] = int(aspect_max * 100)

    cfg["robot_target_x"] = int(rx + cx)
    cfg["robot_target_y"] = int(ry + cy)
    cfg["robot_target_roi_x"] = int(cx)
    cfg["robot_target_roi_y"] = int(cy)

    cfg["last_auto_tune_ts"] = now_ts()
    cfg["last_auto_tune_area"] = round(area, 2)
    cfg["last_auto_tune_aspect"] = round(aspect, 3)
    cfg["last_auto_tune_bbox"] = [int(x), int(y), int(w), int(h)]

    save_config(cfg)

    msg = (
        f"자동 튜닝 완료: V_high={v_high}, "
        f"area={area:.1f}, bbox={w}x{h}, aspect={aspect:.2f}"
    )

    return cfg, mask, info, msg


def detect_robot_with_config(frame, cfg):
    rx, ry, rw, rh = get_roi(frame, cfg)
    roi = frame[ry:ry + rh, rx:rx + rw].copy()

    mask = make_black_mask(roi, cfg)
    contours = find_contours(mask)

    min_area = float(cfg.get("robot_min_area", 200))
    max_area = float(cfg.get("robot_max_area", 50000))
    aspect_min = float(cfg.get("robot_aspect_min_x100", 20)) / 100.0
    aspect_max = float(cfg.get("robot_aspect_max_x100", 400)) / 100.0

    target_rx = cfg.get("robot_target_roi_x", None)
    target_ry = cfg.get("robot_target_roi_y", None)

    candidates = []

    for cnt in contours:
        info = contour_info(cnt)
        area = info["area"]
        aspect = info["aspect"]

        if area < min_area or area > max_area:
            continue

        if aspect < aspect_min or aspect > aspect_max:
            continue

        cx, cy = info["center"]

        if target_rx is not None and target_ry is not None:
            dist = math.sqrt((cx - target_rx) ** 2 + (cy - target_ry) ** 2)
        else:
            dist = 0.0

        # 중요:
        # 기존 코드처럼 "가장 큰 검은 물체"가 아니라
        # "마지막으로 클릭한 로봇 위치에 가까운 후보"를 우선한다.
        score = dist - min(area, 5000) * 0.001

        candidates.append((score, cnt, info))

    candidates.sort(key=lambda item: item[0])

    if candidates:
        return candidates[0][2], mask, len(candidates), (rx, ry, rw, rh)

    return None, mask, 0, (rx, ry, rw, rh)


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        state["click"] = (x, y)
        state["message"] = f"clicked: ({x}, {y}) - press 'a' to auto tune"
        print("[INFO]", state["message"])


def draw(frame, cfg):
    view = frame.copy()

    rx, ry, rw, rh = get_roi(frame, cfg)
    cv2.rectangle(view, (rx, ry), (rx + rw, ry + rh), (255, 255, 0), 2)

    if state["click"] is not None:
        x, y = state["click"]
        cv2.circle(view, (x, y), 6, (0, 255, 255), -1)
        cv2.putText(view, "clicked target", (x + 8, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)

    robot_info, mask, cand_count, roi_tuple = detect_robot_with_config(frame, cfg)

    if robot_info is not None:
        bx, by, bw, bh = robot_info["bbox"]
        cx, cy = robot_info["center"]
        cv2.rectangle(view, (rx + bx, ry + by), (rx + bx + bw, ry + by + bh), (0, 255, 0), 2)
        cv2.circle(view, (rx + cx, ry + cy), 5, (0, 255, 0), -1)
        cv2.putText(view, "robot candidate", (rx + bx, max(20, ry + by - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1, cv2.LINE_AA)

    if cfg.get("robot_target_x") is not None and cfg.get("robot_target_y") is not None:
        tx = int(cfg["robot_target_x"])
        ty = int(cfg["robot_target_y"])
        cv2.drawMarker(view, (tx, ty), (255, 0, 255), cv2.MARKER_CROSS, 16, 2)
        cv2.putText(view, "saved target", (tx + 8, ty + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1, cv2.LINE_AA)

    cv2.rectangle(view, (0, 0), (view.shape[1], 92), (0, 0, 0), -1)
    cv2.putText(view, "Black Robot Auto Tune", (8, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)

    lines = [
        f"message: {state['message']}",
        f"V_high={cfg.get('black_v_high')} min_area={cfg.get('robot_min_area')} max_area={cfg.get('robot_max_area')}",
        f"candidates={cand_count} | r:ROI  a:auto tune  s:save  q:quit"
    ]

    y = 45
    for line in lines:
        cv2.putText(view, line, (8, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
        y += 20

    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    cv2.putText(mask_bgr, "Mask from current config", (8, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)

    return view, mask_bgr


def main():
    cfg = load_config()
    state["cfg"] = cfg

    cap = cv2.VideoCapture(int(cfg.get("camera_index", 0)), cv2.CAP_V4L2)

    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(int(cfg.get("camera_index", 0)))

    if not cap.isOpened():
        print("[ERROR] 카메라를 열 수 없습니다.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(cfg.get("width", 640)))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(cfg.get("height", 480)))

    cv2.namedWindow(WIN_ORIGINAL, cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow(WIN_MASK, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WIN_ORIGINAL, on_mouse)

    print("====================================")
    print("Black Robot Auto Tune v0.1")
    print("1. r : ROI 선택")
    print("2. TurtleBot 중심을 마우스로 클릭")
    print("3. a : 자동 HSV/면적 튜닝")
    print("4. s : 저장")
    print("5. q 또는 ESC : 종료")
    print("====================================")

    last_frame = None

    while True:
        ok, frame = cap.read()

        if not ok or frame is None:
            print("[WARN] frame read failed")
            time.sleep(0.05)
            continue

        last_frame = frame.copy()
        cfg = state["cfg"]

        view, mask_view = draw(frame, cfg)

        cv2.imshow(WIN_ORIGINAL, view)
        cv2.imshow(WIN_MASK, mask_view)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            break

        if key == ord("r"):
            state["cfg"] = select_roi(frame, state["cfg"])
            state["message"] = "ROI selected. Click TurtleBot center."

        if key == ord("a"):
            if last_frame is not None:
                new_cfg, mask, info, msg = auto_tune_from_click(
                    last_frame,
                    state["cfg"],
                    state["click"]
                )
                state["cfg"] = new_cfg
                state["message"] = msg
                print("[INFO]", msg)

        if key == ord("s"):
            save_config(state["cfg"])
            state["message"] = f"saved: {CONFIG_FILE}"
            print("[OK]", state["message"])

    save_config(state["cfg"])
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] 종료. config 저장 완료:", CONFIG_FILE)


if __name__ == "__main__":
    main()
