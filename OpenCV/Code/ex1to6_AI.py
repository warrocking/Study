"""Webcam Canny tuner with OpenCV trackbars.

Controls:
- ESC: quit
- r: reset thresholds (50 / 150)
"""

import cv2


WINDOW_ORIGINAL = "Webcam"
WINDOW_EDGES = "Canny Edges"
TRACKBAR_LOW = "Low"
TRACKBAR_HIGH = "High"


def _noop(_: int) -> None:
    """Trackbar callback placeholder."""
    return


def main() -> None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    cv2.namedWindow(WINDOW_ORIGINAL)
    cv2.namedWindow(WINDOW_EDGES)

    cv2.createTrackbar(TRACKBAR_LOW, WINDOW_EDGES, 50, 255, _noop)
    cv2.createTrackbar(TRACKBAR_HIGH, WINDOW_EDGES, 150, 255, _noop)

    while True:
        ok, frame = cap.read()
        if not ok:
            print("프레임을 읽지 못했습니다.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        low = cv2.getTrackbarPos(TRACKBAR_LOW, WINDOW_EDGES)
        high = cv2.getTrackbarPos(TRACKBAR_HIGH, WINDOW_EDGES)
        if high < low:
            high = low
            cv2.setTrackbarPos(TRACKBAR_HIGH, WINDOW_EDGES, high)

        edges = cv2.Canny(blurred, low, high)

        status = f"low={low} high={high}  (ESC:quit, r:reset)"
        cv2.putText(
            frame,
            status,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow(WINDOW_ORIGINAL, frame)
        cv2.imshow(WINDOW_EDGES, edges)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        if key == ord("r"):
            cv2.setTrackbarPos(TRACKBAR_LOW, WINDOW_EDGES, 50)
            cv2.setTrackbarPos(TRACKBAR_HIGH, WINDOW_EDGES, 150)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
