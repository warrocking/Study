import cv2
import numpy as np


def put_title(image, title):
    """
    화면 왼쪽 위에 필터 이름을 표시하는 함수
    """
    cv2.putText(
        image,
        title,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )
    return image


def main():
    # 0번 카메라를 V4L2 방식으로 열기
    # /dev/video0 과 거의 같은 의미입니다.
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        print("v4l2-ctl --list-devices 명령으로 카메라 번호를 확인하세요.")
        return

    # 카메라 해상도 설정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("카메라 프레임을 읽을 수 없습니다.")
            break

        # 원본 크기 줄이기
        frame = cv2.resize(frame, (320, 240))

        # 1. Grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        gray_bgr = put_title(gray_bgr, "Grayscale")

        # 2. Thresholding
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        threshold_bgr = cv2.cvtColor(threshold, cv2.COLOR_GRAY2BGR)
        threshold_bgr = put_title(threshold_bgr, "Thresholding")

        # 3. Blurring
        blur = cv2.GaussianBlur(frame, (15, 15), 0)
        blur = put_title(blur, "Blurring")

        # 4. Sharpening
        sharpen_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        sharpen = cv2.filter2D(frame, -1, sharpen_kernel)
        sharpen = put_title(sharpen, "Sharpening")

        # 2x2 화면 만들기
        top_row = np.hstack((gray_bgr, threshold_bgr))
        bottom_row = np.hstack((blur, sharpen))
        result = np.vstack((top_row, bottom_row))

        cv2.imshow("OpenCV V4L2 Filter Test", result)

        # q 또는 ESC를 누르면 종료
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
