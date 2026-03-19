import cv2

# ex02 목표:
# 웹캠 영상을 실시간으로 읽어서
# (1) 원본 화면, (2) 색 반전 화면을 동시에 띄워봅니다.

# 0번 카메라(보통 기본 웹캠) 연결 시도
cap = cv2.VideoCapture(0)

# 카메라 장치가 정상적으로 열리지 않으면 종료
if not cap.isOpened():
    print("웹캠이 없습니다.")
    exit()

# ESC 키를 누를 때까지 반복
while True:
    # cap.read() -> (성공여부, 프레임)
    ret, frame = cap.read()

    # 프레임을 못 읽은 경우(카메라 끊김 등) 즉시 종료
    if not ret:
        print("프레임을 읽지 못했습니다.")
        break

    # ~frame : 비트 단위 반전(not)
    # 밝은 곳은 어두워지고, 어두운 곳은 밝아지는 효과
    inverted = ~frame

    # 두 창에 각각 출력
    cv2.imshow("WebCAM", frame)      # 원본
    cv2.imshow("WebCAM_Invert", inverted)  # 반전본

    # 10ms 대기하면서 키 입력 확인
    # ESC(아스키 코드 27)를 누르면 반복 종료
    if cv2.waitKey(10) == 27:
        break

# 사용한 자원 정리(아주 중요)
cap.release()          # 카메라 장치 해제
cv2.destroyAllWindows()  # 모든 창 닫기
