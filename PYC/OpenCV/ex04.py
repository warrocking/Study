import cv2

# ex04 목표:
# 웹캠 프레임에 대해 비트 반전과 absdiff를 적용해
# "원본 vs 반전 vs 차이"를 비교해보는 예제입니다.

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠이 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽지 못했습니다.")
        break

    # bitwise_not: 각 픽셀의 비트를 뒤집어 반전 이미지 생성
    not_frame = cv2.bitwise_not(frame)

    # absdiff: |원본 - 반전|
    # 원본과 반전은 차이가 크기 때문에 강한 대비가 나타납니다.
    abs_diff = cv2.absdiff(frame, not_frame)

    # 화면 출력
    cv2.imshow("WebCAM", frame)
    cv2.imshow("WebCAM_Not", not_frame)
    cv2.imshow("ABS_DIFF", abs_diff)

    # ESC 누르면 종료
    if cv2.waitKey(10) == 27:
        break

cap.release()
cv2.destroyAllWindows()
