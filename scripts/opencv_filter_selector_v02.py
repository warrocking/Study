import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from datetime import datetime
import glob
import math


CONFIG_FILE = Path("opencv_filter_selector_v01_config.json")
SCREENSHOT_DIR = Path("opencv_filter_screenshots")

DEFAULT_CONFIG = {
    "camera_index": 0,
    "tile_w": 320,
    "tile_h": 240,
    "cols": 3,

    "canny_low": 80,
    "canny_high": 160,

    "threshold_value": 127,
    "min_contour_area": 800,

    "h_low": 20,
    "h_high": 35,
    "s_low": 80,
    "s_high": 255,
    "v_low": 80,
    "v_high": 255,

    "hog_every": 10,
    "motion_warn_ratio": 0.05,
    "motion_pause_ratio": 0.15,
    "edge_warn_ratio": 0.04,
    "edge_pause_ratio": 0.10
}


FILTERS = [
    # 기본
    ("original", "Original", "기본", True),
    ("gray", "Grayscale", "기본", False),
    ("clahe", "CLAHE Contrast", "기본", False),
    ("hist_eq", "Histogram Equalization", "기본", False),

    # Blur / 노이즈
    ("gaussian", "Gaussian Blur", "Blur/노이즈", False),
    ("median", "Median Blur", "Blur/노이즈", False),
    ("bilateral", "Bilateral Filter", "Blur/노이즈", False),

    # Edge
    ("canny", "Canny Edge", "Edge/윤곽", True),
    ("sobel_x", "Sobel X", "Edge/윤곽", False),
    ("sobel_y", "Sobel Y", "Edge/윤곽", False),
    ("sobel_mag", "Sobel Magnitude", "Edge/윤곽", False),
    ("laplacian", "Laplacian", "Edge/윤곽", False),
    ("scharr", "Scharr Magnitude", "Edge/윤곽", False),

    # Threshold
    ("binary_thresh", "Binary Threshold", "Threshold", False),
    ("adaptive_thresh", "Adaptive Threshold", "Threshold", False),
    ("otsu_thresh", "Otsu Threshold", "Threshold", False),

    # HSV / 색상
    ("hsv_hue", "HSV Hue", "HSV/색상", False),
    ("hsv_sat", "HSV Saturation", "HSV/색상", False),
    ("hsv_val", "HSV Value", "HSV/색상", False),
    ("hsv_mask", "HSV Mask", "HSV/색상", False),

    # Morphology
    ("morph_open", "Morph Open", "Morphology", False),
    ("morph_close", "Morph Close", "Morphology", False),
    ("morph_gradient", "Morph Gradient", "Morphology", False),

    # Motion / Safety
    ("mog2_mask", "MOG2 Motion Mask", "Motion/Safety", False),
    ("mog2_contours", "MOG2 + Contours", "Motion/Safety", True),
    ("knn_mask", "KNN Motion Mask", "Motion/Safety", False),
    ("frame_diff", "Reference Frame Difference", "Motion/Safety", False),
    ("edge_diff", "Reference Edge Difference", "Motion/Safety", False),
    ("hog_person", "HOG Person Detection", "Motion/Safety", True),
    ("optical_flow", "Optical Flow", "Motion/Safety", False),
    ("safety_summary", "Safety Summary", "Motion/Safety", True)
]


RECOMMENDED_FILTERS = {
    "original",
    "mog2_contours",
    "canny",
    "hog_person",
    "safety_summary"
}


# ============================================================
# 설정
# ============================================================

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


def now_text():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_video_device_numbers():
    devices = []

    for path in sorted(glob.glob("/dev/video*")):
        num = path.replace("/dev/video", "")

        if num.isdigit():
            devices.append(int(num))

    if not devices:
        devices = list(range(0, 4))

    return devices


def to_int(value, default):
    try:
        return int(value)
    except Exception:
        return int(default)


def to_float(value, default):
    try:
        return float(value)
    except Exception:
        return float(default)


# ============================================================
# Tkinter 필터 선택 UI
# ============================================================

class ScrollableFrame(ttk.Frame):
    """
    Tkinter ttk에는 기본 스크롤 Frame이 없어서 Canvas + Frame 조합으로 만든다.
    파라미터 항목이 많을 때 아래쪽이 잘리는 문제를 방지한다.
    """
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_inner_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.inner_id, width=event.width)

    def _on_mousewheel(self, event):
        # 마우스 휠 스크롤
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


class FilterSelector(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("OpenCV Filter Selector v0.2")
        self.geometry("900x700")
        self.minsize(820, 620)

        self.config_data = load_config()
        self.result = None

        self.filter_vars = {}
        self.param_vars = {}

        self._build_ui()

    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        title = ttk.Label(
            root,
            text="OpenCV Filter Selector v0.2",
            font=("Arial", 18, "bold")
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            root,
            text="파라미터는 왼쪽 탭에서 조정하고, 필터는 오른쪽 탭에서 선택한 뒤 Start를 누르세요.",
            font=("Arial", 10)
        )
        subtitle.pack(anchor="w", pady=(0, 10))

        main = ttk.PanedWindow(root, orient="horizontal")
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main, padding=5)
        right = ttk.Frame(main, padding=5)

        main.add(left, weight=1)
        main.add(right, weight=2)

        self._build_param_panel(left)
        self._build_filter_panel(right)

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", pady=(10, 0))

        ttk.Button(
            bottom,
            text="추천 필터 선택",
            command=self.select_recommended
        ).pack(side="left", padx=4)

        ttk.Button(
            bottom,
            text="전체 선택",
            command=self.select_all
        ).pack(side="left", padx=4)

        ttk.Button(
            bottom,
            text="전체 해제",
            command=self.clear_all
        ).pack(side="left", padx=4)

        ttk.Button(
            bottom,
            text="Start",
            command=self.start
        ).pack(side="right", padx=4)

        ttk.Button(
            bottom,
            text="Cancel",
            command=self.cancel
        ).pack(side="right", padx=4)

    # ------------------------------------------------------------
    # 파라미터 패널
    # ------------------------------------------------------------

    def _build_param_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="실행 파라미터", padding=8)
        frame.pack(fill="both", expand=True)

        notebook = ttk.Notebook(frame)
        notebook.pack(fill="both", expand=True)

        tab_basic = ScrollableFrame(notebook)
        tab_edge = ScrollableFrame(notebook)
        tab_hsv = ScrollableFrame(notebook)
        tab_safety = ScrollableFrame(notebook)

        notebook.add(tab_basic, text="기본 실행")
        notebook.add(tab_edge, text="Edge/Threshold")
        notebook.add(tab_hsv, text="HSV 색상")
        notebook.add(tab_safety, text="Safety/HOG")

        self._build_basic_param_tab(tab_basic.inner)
        self._build_edge_param_tab(tab_edge.inner)
        self._build_hsv_param_tab(tab_hsv.inner)
        self._build_safety_param_tab(tab_safety.inner)

    def _add_entry(self, parent, label, key, help_text=None):
        wrapper = ttk.Frame(parent)
        wrapper.pack(fill="x", pady=(0, 7))

        ttk.Label(wrapper, text=label).pack(anchor="w")

        var = tk.StringVar(value=str(self.config_data.get(key, DEFAULT_CONFIG[key])))
        self.param_vars[key] = var

        ttk.Entry(wrapper, textvariable=var).pack(fill="x")

        if help_text:
            ttk.Label(
                wrapper,
                text=help_text,
                foreground="gray",
                font=("Arial", 8)
            ).pack(anchor="w")

    def _build_basic_param_tab(self, parent):
        devices = get_video_device_numbers()

        wrapper = ttk.Frame(parent)
        wrapper.pack(fill="x", pady=(0, 7))

        ttk.Label(wrapper, text="Camera Index").pack(anchor="w")

        cam_var = tk.StringVar(value=str(self.config_data.get("camera_index", 0)))
        self.param_vars["camera_index"] = cam_var

        ttk.Combobox(
            wrapper,
            textvariable=cam_var,
            values=[str(x) for x in devices],
            state="readonly"
        ).pack(fill="x")

        ttk.Label(
            wrapper,
            text="/dev/video0이면 Camera Index 0",
            foreground="gray",
            font=("Arial", 8)
        ).pack(anchor="w")

        self._add_entry(
            parent,
            "Tile Width",
            "tile_w",
            "각 필터 화면 1개의 가로 크기"
        )

        self._add_entry(
            parent,
            "Tile Height",
            "tile_h",
            "각 필터 화면 1개의 세로 크기"
        )

        self._add_entry(
            parent,
            "Columns",
            "cols",
            "한 줄에 표시할 필터 화면 개수"
        )

    def _build_edge_param_tab(self, parent):
        self._add_entry(
            parent,
            "Canny Low",
            "canny_low",
            "Canny edge 하한값. 낮을수록 edge가 많이 잡힘"
        )

        self._add_entry(
            parent,
            "Canny High",
            "canny_high",
            "Canny edge 상한값"
        )

        self._add_entry(
            parent,
            "Threshold Value",
            "threshold_value",
            "Binary threshold 기준값"
        )

        self._add_entry(
            parent,
            "Min Contour Area",
            "min_contour_area",
            "이 면적보다 작은 contour는 노이즈로 무시"
        )

    def _build_hsv_param_tab(self, parent):
        ttk.Label(
            parent,
            text="HSV Mask Range",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(
            parent,
            text="기본값은 노란색 계열 마커/테이프 검출에 가까운 값입니다.",
            foreground="gray",
            font=("Arial", 8)
        ).pack(anchor="w", pady=(0, 8))

        self._add_entry(parent, "H Low", "h_low", "Hue 하한. OpenCV HSV에서 H는 0~179")
        self._add_entry(parent, "H High", "h_high", "Hue 상한")
        self._add_entry(parent, "S Low", "s_low", "Saturation 하한")
        self._add_entry(parent, "S High", "s_high", "Saturation 상한")
        self._add_entry(parent, "V Low", "v_low", "Value 하한")
        self._add_entry(parent, "V High", "v_high", "Value 상한")

    def _build_safety_param_tab(self, parent):
        self._add_entry(
            parent,
            "HOG 실행 간격",
            "hog_every",
            "몇 프레임마다 사람 검출을 실행할지. 작을수록 느려질 수 있음"
        )

        self._add_entry(
            parent,
            "Motion Warn Ratio",
            "motion_warn_ratio",
            "움직임 변화 비율이 이 값 이상이면 WARNING"
        )

        self._add_entry(
            parent,
            "Motion Pause Ratio",
            "motion_pause_ratio",
            "움직임 변화 비율이 이 값 이상이면 PAUSE"
        )

        self._add_entry(
            parent,
            "Edge Warn Ratio",
            "edge_warn_ratio",
            "윤곽 변화 비율이 이 값 이상이면 WARNING"
        )

        self._add_entry(
            parent,
            "Edge Pause Ratio",
            "edge_pause_ratio",
            "윤곽 변화 비율이 이 값 이상이면 PAUSE"
        )

    # ------------------------------------------------------------
    # 필터 선택 패널
    # ------------------------------------------------------------

    def _build_filter_panel(self, parent):
        filter_frame = ttk.LabelFrame(parent, text="필터 선택", padding=8)
        filter_frame.pack(fill="both", expand=True)

        notebook = ttk.Notebook(filter_frame)
        notebook.pack(fill="both", expand=True)

        categories = []

        for _, _, category, _ in FILTERS:
            if category not in categories:
                categories.append(category)

        for category in categories:
            scroll_tab = ScrollableFrame(notebook)
            notebook.add(scroll_tab, text=category)

            for key, name, cat, default_on in FILTERS:
                if cat != category:
                    continue

                var = tk.BooleanVar(value=default_on)
                self.filter_vars[key] = var

                cb = ttk.Checkbutton(
                    scroll_tab.inner,
                    text=name,
                    variable=var
                )
                cb.pack(anchor="w", pady=4)

    # ------------------------------------------------------------
    # 버튼 동작
    # ------------------------------------------------------------

    def select_recommended(self):
        for key, var in self.filter_vars.items():
            var.set(key in RECOMMENDED_FILTERS)

    def select_all(self):
        for var in self.filter_vars.values():
            var.set(True)

    def clear_all(self):
        for var in self.filter_vars.values():
            var.set(False)

    def start(self):
        selected = [key for key, var in self.filter_vars.items() if var.get()]

        if not selected:
            messagebox.showwarning("필터 선택 필요", "최소 1개 이상의 필터를 선택하세요.")
            return

        params = {}

        for key, var in self.param_vars.items():
            value = var.get().strip()
            params[key] = value

        config_to_save = dict(DEFAULT_CONFIG)

        for key, value in params.items():
            default = DEFAULT_CONFIG.get(key)

            if isinstance(default, int):
                config_to_save[key] = to_int(value, default)
            elif isinstance(default, float):
                config_to_save[key] = to_float(value, default)
            else:
                config_to_save[key] = value

        save_config(config_to_save)

        self.result = {
            "selected": selected,
            "params": config_to_save
        }

        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


# ============================================================
# OpenCV 화면 유틸
# ============================================================

def ensure_bgr(img):
    if img is None:
        img = np.zeros((240, 320, 3), dtype=np.uint8)

    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    if img.shape[2] == 1:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    return img


def add_label(img, title, lines=None):
    out = ensure_bgr(img).copy()

    cv2.rectangle(out, (0, 0), (out.shape[1], 28), (0, 0, 0), -1)
    cv2.putText(
        out,
        title,
        (8, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    if lines:
        y = 48

        for line in lines:
            cv2.putText(
                out,
                str(line),
                (8, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1,
                cv2.LINE_AA
            )
            y += 22

    return out


def resize_tile(img, tile_w, tile_h):
    img = ensure_bgr(img)
    return cv2.resize(img, (tile_w, tile_h), interpolation=cv2.INTER_AREA)


def make_grid(tiles, tile_w, tile_h, cols):
    if not tiles:
        blank = np.zeros((tile_h, tile_w, 3), dtype=np.uint8)
        return add_label(blank, "No Filter Selected")

    cols = max(1, int(cols))
    rows = math.ceil(len(tiles) / cols)

    blank = np.zeros((tile_h, tile_w, 3), dtype=np.uint8)
    grid_rows = []

    idx = 0

    for _ in range(rows):
        row_imgs = []

        for _ in range(cols):
            if idx < len(tiles):
                row_imgs.append(resize_tile(tiles[idx], tile_w, tile_h))
            else:
                row_imgs.append(blank.copy())

            idx += 1

        grid_rows.append(np.hstack(row_imgs))

    return np.vstack(grid_rows)


def colorize_gray(gray, colormap=cv2.COLORMAP_JET):
    gray_u8 = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    gray_u8 = np.uint8(gray_u8)
    return cv2.applyColorMap(gray_u8, colormap)


def draw_contours_on_frame(frame, mask, min_area):
    out = frame.copy()

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    count = 0
    area_sum = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(
            out,
            f"{int(area)}",
            (x, max(15, y - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1,
            cv2.LINE_AA
        )

        count += 1
        area_sum += area

    return out, count, area_sum


# ============================================================
# 필터 처리기
# ============================================================

class FilterProcessor:
    def __init__(self, params):
        self.params = params

        self.mog2 = cv2.createBackgroundSubtractorMOG2(
            history=300,
            varThreshold=25,
            detectShadows=True
        )

        self.knn = cv2.createBackgroundSubtractorKNN(
            history=300,
            dist2Threshold=400,
            detectShadows=True
        )

        self.prev_gray = None
        self.ref_gray = None
        self.ref_edges = None

        self.frame_count = 0

        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.last_hog_boxes = []

    def reset_reference(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        self.ref_gray = gray

        low = int(self.params["canny_low"])
        high = int(self.params["canny_high"])
        self.ref_edges = cv2.Canny(gray, low, high)

    def clean_mask(self, mask):
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.medianBlur(mask, 5)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return mask

    def get_hog_boxes(self, frame):
        hog_every = max(1, int(self.params["hog_every"]))

        if self.frame_count % hog_every == 0:
            small = cv2.resize(frame, None, fx=0.75, fy=0.75)

            boxes, weights = self.hog.detectMultiScale(
                small,
                winStride=(8, 8),
                padding=(8, 8),
                scale=1.05
            )

            scale_back = 1.0 / 0.75
            scaled_boxes = []

            for (x, y, w, h) in boxes:
                scaled_boxes.append((
                    int(x * scale_back),
                    int(y * scale_back),
                    int(w * scale_back),
                    int(h * scale_back)
                ))

            self.last_hog_boxes = scaled_boxes

        return self.last_hog_boxes

    def compute(self, frame, selected):
        self.frame_count += 1

        if self.ref_gray is None or self.ref_edges is None:
            self.reset_reference(frame)

        tile_outputs = []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_gray = cv2.GaussianBlur(gray, (5, 5), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        low = int(self.params["canny_low"])
        high = int(self.params["canny_high"])
        min_area = float(self.params["min_contour_area"])

        canny = None
        mog2_mask = None
        knn_mask = None
        hog_boxes = None

        need_canny = (
            "canny" in selected
            or "edge_diff" in selected
            or "canny_contours" in selected
            or "safety_summary" in selected
        )

        if need_canny:
            canny = cv2.Canny(blur_gray, low, high)

        need_mog2 = (
            "mog2_mask" in selected
            or "mog2_contours" in selected
            or "safety_summary" in selected
        )

        if need_mog2:
            mog2_mask = self.mog2.apply(frame)
            _, mog2_mask = cv2.threshold(mog2_mask, 200, 255, cv2.THRESH_BINARY)
            mog2_mask = self.clean_mask(mog2_mask)

        need_knn = "knn_mask" in selected

        if need_knn:
            knn_mask = self.knn.apply(frame)
            _, knn_mask = cv2.threshold(knn_mask, 200, 255, cv2.THRESH_BINARY)
            knn_mask = self.clean_mask(knn_mask)

        need_hog = "hog_person" in selected or "safety_summary" in selected

        if need_hog:
            hog_boxes = self.get_hog_boxes(frame)

        motion_ratio = 0.0
        edge_ratio = 0.0
        person_count = 0

        if mog2_mask is not None:
            motion_ratio = cv2.countNonZero(mog2_mask) / float(mog2_mask.size)

        if canny is not None and self.ref_edges is not None:
            edge_diff = cv2.absdiff(canny, self.ref_edges)
            edge_ratio = cv2.countNonZero(edge_diff) / float(edge_diff.size)

        if hog_boxes is not None:
            person_count = len(hog_boxes)

        # ---------------- 기본 ----------------

        if "original" in selected:
            lines = [
                f"FPS frame: {self.frame_count}",
                "q: quit, r: reset reference, s: screenshot"
            ]
            tile_outputs.append(add_label(frame, "Original", lines))

        if "gray" in selected:
            tile_outputs.append(add_label(gray, "Grayscale"))

        if "clahe" in selected:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            out = clahe.apply(gray)
            tile_outputs.append(add_label(out, "CLAHE Contrast"))

        if "hist_eq" in selected:
            out = cv2.equalizeHist(gray)
            tile_outputs.append(add_label(out, "Histogram Equalization"))

        # ---------------- Blur ----------------

        if "gaussian" in selected:
            out = cv2.GaussianBlur(frame, (15, 15), 0)
            tile_outputs.append(add_label(out, "Gaussian Blur"))

        if "median" in selected:
            out = cv2.medianBlur(frame, 9)
            tile_outputs.append(add_label(out, "Median Blur"))

        if "bilateral" in selected:
            out = cv2.bilateralFilter(frame, 9, 75, 75)
            tile_outputs.append(add_label(out, "Bilateral Filter"))

        # ---------------- Edge ----------------

        if "canny" in selected:
            tile_outputs.append(add_label(canny, "Canny Edge", [
                f"low={low}, high={high}"
            ]))

        if "sobel_x" in selected:
            sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sx = cv2.convertScaleAbs(sx)
            tile_outputs.append(add_label(sx, "Sobel X"))

        if "sobel_y" in selected:
            sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sy = cv2.convertScaleAbs(sy)
            tile_outputs.append(add_label(sy, "Sobel Y"))

        if "sobel_mag" in selected:
            sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            mag = cv2.magnitude(sx, sy)
            out = colorize_gray(mag)
            tile_outputs.append(add_label(out, "Sobel Magnitude"))

        if "laplacian" in selected:
            lap = cv2.Laplacian(gray, cv2.CV_64F)
            lap = cv2.convertScaleAbs(lap)
            tile_outputs.append(add_label(lap, "Laplacian"))

        if "scharr" in selected:
            sx = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
            sy = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
            mag = cv2.magnitude(sx, sy)
            out = colorize_gray(mag)
            tile_outputs.append(add_label(out, "Scharr Magnitude"))

        # ---------------- Threshold ----------------

        if "binary_thresh" in selected:
            t = int(self.params["threshold_value"])
            _, out = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
            tile_outputs.append(add_label(out, "Binary Threshold", [f"threshold={t}"]))

        if "adaptive_thresh" in selected:
            out = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            tile_outputs.append(add_label(out, "Adaptive Threshold"))

        if "otsu_thresh" in selected:
            _, out = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            tile_outputs.append(add_label(out, "Otsu Threshold"))

        # ---------------- HSV ----------------

        if "hsv_hue" in selected:
            hue = hsv[:, :, 0]
            out = cv2.applyColorMap(np.uint8(hue * 255 / 179), cv2.COLORMAP_HSV)
            tile_outputs.append(add_label(out, "HSV Hue"))

        if "hsv_sat" in selected:
            sat = hsv[:, :, 1]
            tile_outputs.append(add_label(sat, "HSV Saturation"))

        if "hsv_val" in selected:
            val = hsv[:, :, 2]
            tile_outputs.append(add_label(val, "HSV Value"))

        if "hsv_mask" in selected:
            h_low = int(self.params["h_low"])
            h_high = int(self.params["h_high"])
            s_low = int(self.params["s_low"])
            s_high = int(self.params["s_high"])
            v_low = int(self.params["v_low"])
            v_high = int(self.params["v_high"])

            if h_low <= h_high:
                lower = np.array([h_low, s_low, v_low])
                upper = np.array([h_high, s_high, v_high])
                mask = cv2.inRange(hsv, lower, upper)
            else:
                lower1 = np.array([0, s_low, v_low])
                upper1 = np.array([h_high, s_high, v_high])
                lower2 = np.array([h_low, s_low, v_low])
                upper2 = np.array([179, s_high, v_high])
                mask = cv2.bitwise_or(
                    cv2.inRange(hsv, lower1, upper1),
                    cv2.inRange(hsv, lower2, upper2)
                )

            out = cv2.bitwise_and(frame, frame, mask=mask)
            tile_outputs.append(add_label(out, "HSV Mask", [
                f"H={h_low}~{h_high}",
                f"S={s_low}~{s_high}",
                f"V={v_low}~{v_high}"
            ]))

        # ---------------- Morphology ----------------

        kernel = np.ones((5, 5), np.uint8)
        _, base_bin = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        if "morph_open" in selected:
            out = cv2.morphologyEx(base_bin, cv2.MORPH_OPEN, kernel)
            tile_outputs.append(add_label(out, "Morph Open"))

        if "morph_close" in selected:
            out = cv2.morphologyEx(base_bin, cv2.MORPH_CLOSE, kernel)
            tile_outputs.append(add_label(out, "Morph Close"))

        if "morph_gradient" in selected:
            out = cv2.morphologyEx(base_bin, cv2.MORPH_GRADIENT, kernel)
            tile_outputs.append(add_label(out, "Morph Gradient"))

        # ---------------- Motion / Safety ----------------

        if "mog2_mask" in selected:
            tile_outputs.append(add_label(mog2_mask, "MOG2 Motion Mask", [
                f"motion_ratio={motion_ratio:.3f}"
            ]))

        if "mog2_contours" in selected:
            out, count, area_sum = draw_contours_on_frame(frame, mog2_mask, min_area)
            tile_outputs.append(add_label(out, "MOG2 + Contours", [
                f"objects={count}",
                f"motion_ratio={motion_ratio:.3f}",
                f"area_sum={int(area_sum)}"
            ]))

        if "knn_mask" in selected:
            ratio = cv2.countNonZero(knn_mask) / float(knn_mask.size)
            tile_outputs.append(add_label(knn_mask, "KNN Motion Mask", [
                f"motion_ratio={ratio:.3f}"
            ]))

        if "frame_diff" in selected:
            diff = cv2.absdiff(blur_gray, self.ref_gray)
            _, diff_mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            diff_mask = self.clean_mask(diff_mask)

            ratio = cv2.countNonZero(diff_mask) / float(diff_mask.size)

            out, count, area_sum = draw_contours_on_frame(frame, diff_mask, min_area)
            tile_outputs.append(add_label(out, "Reference Frame Difference", [
                f"change_ratio={ratio:.3f}",
                f"objects={count}",
                "r: reset reference"
            ]))

        if "edge_diff" in selected:
            diff = cv2.absdiff(canny, self.ref_edges)
            ratio = cv2.countNonZero(diff) / float(diff.size)

            out = colorize_gray(diff)
            tile_outputs.append(add_label(out, "Reference Edge Difference", [
                f"edge_change_ratio={ratio:.3f}",
                "r: reset reference"
            ]))

        if "hog_person" in selected:
            out = frame.copy()

            for (x, y, w, h) in hog_boxes:
                cv2.rectangle(out, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(
                    out,
                    "person",
                    (x, max(15, y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 255),
                    1,
                    cv2.LINE_AA
                )

            tile_outputs.append(add_label(out, "HOG Person Detection", [
                f"person_count={len(hog_boxes)}",
                f"every {self.params['hog_every']} frames"
            ]))

        if "optical_flow" in selected:
            out = frame.copy()

            small_gray = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)

            if self.prev_gray is not None:
                prev_small = cv2.resize(self.prev_gray, (0, 0), fx=0.5, fy=0.5)

                flow = cv2.calcOpticalFlowFarneback(
                    prev_small,
                    small_gray,
                    None,
                    0.5,
                    3,
                    15,
                    3,
                    5,
                    1.2,
                    0
                )

                step = 16

                for y in range(0, flow.shape[0], step):
                    for x in range(0, flow.shape[1], step):
                        fx, fy = flow[y, x]
                        x1 = int(x * 2)
                        y1 = int(y * 2)
                        x2 = int((x + fx) * 2)
                        y2 = int((y + fy) * 2)

                        cv2.arrowedLine(
                            out,
                            (x1, y1),
                            (x2, y2),
                            (0, 255, 0),
                            1,
                            tipLength=0.3
                        )

            tile_outputs.append(add_label(out, "Optical Flow"))

        if "safety_summary" in selected:
            event_level = "NORMAL"
            event_reason = "none"

            motion_warn = float(self.params["motion_warn_ratio"])
            motion_pause = float(self.params["motion_pause_ratio"])
            edge_warn = float(self.params["edge_warn_ratio"])
            edge_pause = float(self.params["edge_pause_ratio"])

            if person_count > 0:
                event_level = "PAUSE"
                event_reason = "person_detected"
            elif motion_ratio >= motion_pause:
                event_level = "PAUSE"
                event_reason = "large_motion_change"
            elif edge_ratio >= edge_pause:
                event_level = "PAUSE"
                event_reason = "large_edge_change"
            elif motion_ratio >= motion_warn:
                event_level = "WARNING"
                event_reason = "motion_change"
            elif edge_ratio >= edge_warn:
                event_level = "WARNING"
                event_reason = "edge_change"

            out = np.zeros_like(frame)

            lines = [
                f"event_level: {event_level}",
                f"reason: {event_reason}",
                f"motion_ratio: {motion_ratio:.3f}",
                f"edge_ratio: {edge_ratio:.3f}",
                f"person_count: {person_count}",
                "This is event detection only.",
                "ROS2 stop is not connected yet."
            ]

            tile_outputs.append(add_label(out, "Safety Summary", lines))

        self.prev_gray = blur_gray.copy()

        return tile_outputs


# ============================================================
# 메인 실행
# ============================================================

def open_camera(index):
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)

    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(index)

    if not cap.isOpened():
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    return cap


def run_opencv(selected, params):
    camera_index = int(params["camera_index"])
    tile_w = int(params["tile_w"])
    tile_h = int(params["tile_h"])
    cols = int(params["cols"])

    cap = open_camera(camera_index)

    if cap is None:
        print(f"[ERROR] 카메라를 열 수 없습니다: /dev/video{camera_index}")
        return

    processor = FilterProcessor(params)

    paused = False
    last_grid = None

    print("====================================")
    print("OpenCV Filter Viewer Started")
    print("q 또는 ESC : 종료")
    print("r : 기준 프레임 재설정")
    print("s : 현재 화면 저장")
    print("p : 일시정지/재개")
    print("====================================")

    while True:
        if not paused:
            ok, frame = cap.read()

            if not ok or frame is None:
                print("[WARN] 프레임 읽기 실패")
                continue

            tiles = processor.compute(frame, selected)
            grid = make_grid(tiles, tile_w, tile_h, cols)
            last_grid = grid

        else:
            grid = last_grid

        if grid is None:
            continue

        cv2.imshow("OpenCV Filter Selector v0.1", grid)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            break

        if key == ord("p"):
            paused = not paused
            print("[INFO] pause =", paused)

        if key == ord("r"):
            if not paused:
                processor.reset_reference(frame)
                processor.mog2 = cv2.createBackgroundSubtractorMOG2(
                    history=300,
                    varThreshold=25,
                    detectShadows=True
                )
                processor.knn = cv2.createBackgroundSubtractorKNN(
                    history=300,
                    dist2Threshold=400,
                    detectShadows=True
                )
                print("[INFO] reference frame reset")

        if key == ord("s"):
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            path = SCREENSHOT_DIR / f"filter_view_{now_text()}.png"
            cv2.imwrite(str(path), grid)
            print(f"[INFO] screenshot saved: {path}")

    cap.release()
    cv2.destroyAllWindows()


def main():
    app = FilterSelector()
    app.mainloop()

    if app.result is None:
        print("[INFO] 사용자가 실행을 취소했습니다.")
        return

    selected = app.result["selected"]
    params = app.result["params"]

    print("[INFO] 선택한 필터:")
    for item in selected:
        print(" -", item)

    run_opencv(selected, params)


if __name__ == "__main__":
    main()
