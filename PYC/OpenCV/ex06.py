import cv2

# ex06 목표:
# 웹캠 영상에서 실시간으로 Canny 엣지(경계선) 검출하기

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠이 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽지 못했습니다.")
        break

    # Canny는 보통 그레이스케일에서 먼저 처리하면 결과가 안정적입니다.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # threshold 값은 환경(조명, 카메라 화질)에 따라 조절이 필요합니다.
    # 값이 낮으면 엣지가 많이 잡히고, 높으면 강한 윤곽만 남습니다.
    canny_image = cv2.Canny(gray, 40.0, 160.0)

    # 원본과 엣지 결과를 동시에 확인
    cv2.imshow("WebCAM", frame)
    cv2.imshow("Edge", canny_image)

    # ESC 키로 종료
    if cv2.waitKey(10) == 27:
        break

cap.release()
cv2.destroyAllWindows()
