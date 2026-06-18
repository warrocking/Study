import cv2
import numpy as np


# ==============================
# 사용자가 바꿀 수 있는 설정
# ==============================

DEVICE_PATH = "/dev/video0"   # 안 되면 "/dev/video1" 로 변경
CAM_WIDTH = 640
CAM_HEIGHT = 480

TILE_WIDTH = 200
TILE_HEIGHT = 150
GRID_COLS = 5

WINDOW_NAME = "OpenCV V4L2 All Filter Test"


# ==============================
# 보조 함수들
# ==============================

def to_bgr(image):
    """
    OpenCV 화면 합치기를 위해 이미지를 항상 BGR 3채널로 맞추는 함수
    """
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def make_tile(image, title):
    """
    각 필터 결과를 같은 크기로 만들고 제목을 붙이는 함수
    """
    image = to_bgr(image)
    image = cv2.resize(image, (TILE_WIDTH, TILE_HEIGHT))

    cv2.rectangle(image, (0, 0), (TILE_WIDTH, 28), (0, 0, 0), -1)
    cv2.putText(
        image,
        title,
        (8, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 0),
        1,
        cv2.LINE_AA
    )

    return image


def make_grid(tile_list, cols):
    """
    여러 필터 화면을 격자 형태로 합치는 함수
    """
    rows = []

    for i in range(0, len(tile_list), cols):
        row_tiles = tile_list[i:i + cols]

        while len(row_tiles) < cols:
            blank = np.zeros((TILE_HEIGHT, TILE_WIDTH, 3), dtype=np.uint8)
            row_tiles.append(blank)

        rows.append(np.hstack(row_tiles))

    return np.vstack(rows)


def main():
    cap = cv2.VideoCapture(DEVICE_PATH, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        print("DEVICE_PATH를 /dev/video0 또는 /dev/video1 로 바꿔보세요.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("카메라 프레임을 읽을 수 없습니다.")
            break

        # 너무 큰 화면을 매 프레임 처리하면 느려지므로 내부 처리용 크기로 줄임
        frame = cv2.resize(frame, (320, 240))

        # ==============================
        # 기본 색상 변환
        # ==============================

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # HSV의 Hue 채널만 보기
        hue = hsv[:, :, 0]

        # ==============================
        # Threshold 계열
        # ==============================

        _, threshold = cv2.threshold(
            gray,
            127,
            255,
            cv2.THRESH_BINARY
        )

        adaptive_threshold = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        otsu_value, otsu_threshold = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # ==============================
        # 색상 마스크 계열
        # 빨간색 물체가 있으면 잘 보임
        # ==============================

        lower_red_1 = np.array([0, 100, 100])
        upper_red_1 = np.array([10, 255, 255])

        lower_red_2 = np.array([170, 100, 100])
        upper_red_2 = np.array([180, 255, 255])

        red_mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
        red_mask_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
        red_mask = cv2.bitwise_or(red_mask_1, red_mask_2)

        red_only = cv2.bitwise_and(frame, frame, mask=red_mask)

        # ==============================
        # Blurring / Smoothing 계열
        # ==============================

        average_blur = cv2.blur(frame, (9, 9))

        gaussian_blur = cv2.GaussianBlur(
            frame,
            (9, 9),
            0
        )

        median_blur = cv2.medianBlur(
            frame,
            9
        )

        bilateral = cv2.bilateralFilter(
            frame,
            9,
            75,
            75
        )

        # 고급 노이즈 제거
        # 실시간에서는 무거울 수 있음
        denoised = cv2.fastNlMeansDenoisingColored(
            frame,
            None,
            7,
            7,
            7,
            21
        )

        # ==============================
        # Sharpening / Custom Kernel 계열
        # ==============================

        sharpen_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        sharpen = cv2.filter2D(
            frame,
            -1,
            sharpen_kernel
        )

        emboss_kernel = np.array([
            [-2, -1, 0],
            [-1, 1, 1],
            [0, 1, 2]
        ])

        emboss = cv2.filter2D(
            frame,
            -1,
            emboss_kernel
        )

        # ==============================
        # Edge Detection 계열
        # ==============================

        canny = cv2.Canny(
            gaussian_blur,
            100,
            200
        )

        sobel_x = cv2.Sobel(
            gray,
            cv2.CV_64F,
            1,
            0,
            ksize=3
        )
        sobel_x = cv2.convertScaleAbs(sobel_x)

        sobel_y = cv2.Sobel(
            gray,
            cv2.CV_64F,
            0,
            1,
            ksize=3
        )
        sobel_y = cv2.convertScaleAbs(sobel_y)

        sobel_x_64 = cv2.Sobel(
            gray,
            cv2.CV_64F,
            1,
            0,
            ksize=3
        )

        sobel_y_64 = cv2.Sobel(
            gray,
            cv2.CV_64F,
            0,
            1,
            ksize=3
        )

        sobel_magnitude = cv2.magnitude(
            sobel_x_64,
            sobel_y_64
        )

        sobel_magnitude = cv2.normalize(
            sobel_magnitude,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        laplacian = cv2.Laplacian(
            gray,
            cv2.CV_64F
        )
        laplacian = cv2.convertScaleAbs(laplacian)

        # ==============================
        # Morphology 계열
        # 보통 흑백 이미지에서 사용
        # ==============================

        morph_kernel = np.ones((5, 5), np.uint8)

        erosion = cv2.erode(
            threshold,
            morph_kernel,
            iterations=1
        )

        dilation = cv2.dilate(
            threshold,
            morph_kernel,
            iterations=1
        )

        opening = cv2.morphologyEx(
            threshold,
            cv2.MORPH_OPEN,
            morph_kernel
        )

        closing = cv2.morphologyEx(
            threshold,
            cv2.MORPH_CLOSE,
            morph_kernel
        )

        morph_gradient = cv2.morphologyEx(
            threshold,
            cv2.MORPH_GRADIENT,
            morph_kernel
        )

        # ==============================
        # Histogram / Contrast 계열
        # ==============================

        equalized = cv2.equalizeHist(gray)

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )
        clahe_result = clahe.apply(gray)

        # ==============================
        # Contour 검출
        # ==============================

        contours, _ = cv2.findContours(
            closing,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        contour_result = frame.copy()

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < 300:
                continue

            cv2.drawContours(
                contour_result,
                [contour],
                -1,
                (0, 255, 0),
                2
            )

            x, y, w, h = cv2.boundingRect(contour)

            cv2.rectangle(
                contour_result,
                (x, y),
                (x + w, y + h),
                (255, 0, 0),
                2
            )

        # ==============================
        # Geometric Transform 계열
        # ==============================

        flip_horizontal = cv2.flip(frame, 1)

        rotate_90 = cv2.rotate(
            frame,
            cv2.ROTATE_90_CLOCKWISE
        )

        h, w = frame.shape[:2]
        center = (w // 2, h // 2)

        rotate_matrix = cv2.getRotationMatrix2D(
            center,
            20,
            1.0
        )

        warp_affine = cv2.warpAffine(
            frame,
            rotate_matrix,
            (w, h)
        )

        src_points = np.float32([
            [40, 30],
            [w - 40, 30],
            [30, h - 30],
            [w - 30, h - 30]
        ])

        dst_points = np.float32([
            [0, 0],
            [w, 0],
            [0, h],
            [w, h]
        ])

        perspective_matrix = cv2.getPerspectiveTransform(
            src_points,
            dst_points
        )

        warp_perspective = cv2.warpPerspective(
            frame,
            perspective_matrix,
            (w, h)
        )

        # ==============================
        # 타일 목록 만들기
        # ==============================

        tiles = [
            make_tile(frame, "Original"),
            make_tile(gray, "Grayscale"),
            make_tile(hue, "HSV Hue"),

            make_tile(threshold, "Threshold"),
            make_tile(adaptive_threshold, "Adaptive Th"),
            make_tile(otsu_threshold, f"Otsu Th {otsu_value:.0f}"),

            make_tile(red_mask, "Red Mask"),
            make_tile(red_only, "Red Only"),

            make_tile(average_blur, "Average Blur"),
            make_tile(gaussian_blur, "Gaussian Blur"),
            make_tile(median_blur, "Median Blur"),
            make_tile(bilateral, "Bilateral"),
            make_tile(denoised, "Denoising"),

            make_tile(sharpen, "Sharpen"),
            make_tile(emboss, "Emboss Kernel"),

            make_tile(canny, "Canny"),
            make_tile(sobel_x, "Sobel X"),
            make_tile(sobel_y, "Sobel Y"),
            make_tile(sobel_magnitude, "Sobel Mag"),
            make_tile(laplacian, "Laplacian"),

            make_tile(erosion, "Erosion"),
            make_tile(dilation, "Dilation"),
            make_tile(opening, "Opening"),
            make_tile(closing, "Closing"),
            make_tile(morph_gradient, "Morph Gradient"),

            make_tile(equalized, "Equalize Hist"),
            make_tile(clahe_result, "CLAHE"),

            make_tile(contour_result, "Contours"),

            make_tile(flip_horizontal, "Flip"),
            make_tile(rotate_90, "Rotate 90"),
            make_tile(warp_affine, "Warp Affine"),
            make_tile(warp_perspective, "Perspective"),
        ]

        grid = make_grid(tiles, GRID_COLS)

        cv2.imshow(WINDOW_NAME, grid)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
