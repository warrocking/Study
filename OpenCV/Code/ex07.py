"""
    제작 시간 : 0318_09:24
    유형 : 예제
    주제 : 웹캠 모션 감지로 공 터치 게임 만들기
    문제 설명 :
    - 화면에 빨간 공이 랜덤 위치에 생성됨
    - 손을 움직여 공 영역에서 움직임이 감지되면 점수 +1
    - 공은 새 위치로 이동

    핵심 학습 포인트:
    1) 프레임 기반 처리(while 루프에서 웹캠 영상 계속 읽기)
    2) 움직임 감지(absdiff + threshold)
    3) ROI(관심 영역)만 잘라서 충돌 판정
"""

# 기본 모듈
import sys
# 참고: 현재 코드에서는 sys를 직접 쓰지 않지만,
# 이후 sys.exit() 같은 종료 처리 확장 시 사용할 수 있어 남겨둠

import cv2
import numpy as np
# 참고: 현재 코드에서는 numpy(np)를 직접 쓰지 않지만,
# OpenCV는 내부적으로 ndarray(넘파이 배열)를 다루므로 같이 배우는 경우가 많음

# 개념 메모
# ROI: Region Of Interest, "관심 영역"만 잘라서 계산량을 줄이는 기법
# 추적: 프레임 간 차이를 통해 움직인 위치를 찾는 아이디어
# 과거 프레임 + 현재 프레임 둘 다 있어야 "변화량" 계산 가능
# Filter: 노이즈 제거용 전처리(여기서는 GaussianBlur)
# ABSFILTER: absdiff(절대값 차이) 기반 움직임 비교

# 목표
# 화면에 공이 랜덤하게 생기고, 손으로 공 위치에서 움직임을 만들면
# 공을 맞춘 것으로 판정해서 점수를 누적하는 게임


class Ball:
    def __init__(self):
        # object의 생성자를 호출
        # 참고: 파이썬 기본 클래스만 상속할 때는 없어도 동작함
        super().__init__()

        print("Ball object created")

        # 공 반지름(픽셀 단위)
        self.radius = 0

        # 공 중심 좌표 (x, y)
        (self.x, self.y) = (0, 0)

        # 공 활성화 여부
        # True면 충돌 판정을 수행하고 화면에 그림
        self.is_Activate = False

    def __del__(self):
        print("A ball object deleted")
        # 참고: __del__은 호출 시점이 파이썬 메모리 관리 상황에 따라 달라질 수 있음


# 랜덤한 위치를 생성하는 함수
import random


def get_random_position(frame_width, frame_height, radius) -> tuple:
    # 공 중심 좌표를 랜덤으로 뽑음
    # radius를 경계에 반영해야 공이 화면 밖으로 튀어나가지 않음
    x = random.randint(radius, frame_width - radius)
    y = random.randint(radius, frame_height - radius)
    return (x, y)



def main() -> None:

    # 0번 카메라(보통 기본 웹캠) 열기
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print("Can't open Camera")
        return
    else:
        pass
        # 참고: else: pass는 없어도 됨 (if에서 return 하므로 아래 코드는 자동 진행)

    # 현재 카메라 해상도(가로/세로) 확인
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("W : {} , H : {}".format(frame_width, frame_height))

    # 빨간 공 객체 생성 + 초기 설정
    red_ball = Ball()
    red_ball.radius = 40
    (red_ball.x, red_ball.y) = get_random_position(frame_width, frame_height, red_ball.radius)
    red_ball.is_Activate = True

    # 게임 상태 변수
    score = 0

    # 이전 프레임 저장 변수
    # 왜 필요한가?
    # "현재 프레임만" 보면 움직임인지 배경인지 구분이 어렵고,
    # "이전 프레임과의 차이"를 봐야 실제 움직임을 찾을 수 있음
    pre_gray_frame = None

    while(True):
        # 웹캠에서 프레임 1장 읽기
        ref, frame = capture.read()

        if frame is None:
            print("Can't capture frame")
            # 참고(개선 포인트): 여기서 break 하면 아래 cv2.flip 에러를 예방 가능

        # 좌우 반전(거울처럼 보이게 해서 사용감 개선)
        frame = cv2.flip(frame, 1)

        # 컬러(BGR) -> 그레이스케일
        # 이유: 연산량 감소 + 밝기 변화 기반 비교가 쉬움
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 참고: OpenCV 색상 순서는 RGB가 아니라 BGR

        # 가우시안 블러로 작은 노이즈 제거
        # 노이즈가 줄어들면 absdiff 결과가 덜 들쭉날쭉해져 감지가 안정적
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
        # (21, 21): 커널 크기(홀수여야 함), 값이 클수록 더 강하게 부드러워짐

        # 첫 프레임은 이전 프레임이 없으므로 비교 불가
        # 저장만 하고 다음 루프로 넘어감
        if pre_gray_frame is None:
            pre_gray_frame = gray_frame.copy()
            continue

        # 움직임 감지 핵심: |이전 - 현재|
        # 값이 클수록 해당 위치에서 변화(움직임)가 컸다는 뜻
        diff_frame = cv2.absdiff(pre_gray_frame, gray_frame)

        # threshold(이진화): 작은 변화는 0, 큰 변화는 255로 단순화
        # 이렇게 해야 움직인 픽셀 수를 쉽게 셀 수 있음
        # ref는 threshold가 실제 사용한 임계값 반환값(현재 코드에서는 미사용)
        # 참고(개선 포인트): ref 대신 _ 를 쓰면 "미사용 값" 의도가 더 명확함
        ref, thresh_frame = cv2.threshold(diff_frame, 25, 255, cv2.THRESH_BINARY)

        # 공이 활성화되어 있을 때만 충돌 판정
        if red_ball.is_Activate:
            # 공 중심/반지름으로 공 주변 사각형 ROI 계산
            (x1, y1) = (max(0, red_ball.x - red_ball.radius), max(0, red_ball.y - red_ball.radius))
            (x2, y2) = (min(frame_width, red_ball.x + red_ball.radius), min(frame_height, red_ball.y + red_ball.radius))

            # 현재 판정 영역을 시각적으로 표시
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 전체 화면이 아니라 ROI만 잘라서 계산
            roi = thresh_frame[y1:y2, x1:x2]

            # roi에서 0이 아닌(흰색=움직임) 픽셀 개수 세기
            movement_pixel = cv2.countNonZero(roi)

            # ROI 총 면적
            area = (x2 - x1) * (y2 - y1)

            # 움직인 픽셀이 ROI의 10%를 넘으면 "터치 성공"
            # 0.1(10%) 값은 민감도: 낮추면 더 쉽게 맞고, 높이면 더 어렵게 맞음
            if movement_pixel > area * 0.2:
                score += 1
                print("터치 성공 - 점수 : {}".format(score))

                # 맞췄으면 다음 공을 새 랜덤 위치에 생성
                (red_ball.x, red_ball.y) = get_random_position(frame_width, frame_height, red_ball.radius)

        # 빨간 공 그리기
        # 색상은 BGR 순서이므로 빨강 = (0, 0, 255)
        # thickness=-1 은 내부를 채운 원
        cv2.circle(frame, (red_ball.x, red_ball.y), red_ball.radius, (0, 0, 255), -1)

        # 점수 텍스트 출력
        cv2.putText(frame, "Score : {}".format(score), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 최종 프레임 화면 출력
        cv2.imshow("HIT BALL", frame)

        # 현재 프레임을 다음 루프의 "이전 프레임"으로 저장
        pre_gray_frame = gray_frame.copy()

        # ESC(27) 누르면 종료
        if cv2.waitKey(20) == 27:
            break

    # 자원 정리(카메라 잠금 해제 + 창 닫기)
    capture.release()
    cv2.destroyAllWindows()
    return None


if __name__ == "__main__":
    main()
    pass
    # 참고: main() 아래 pass도 없어도 되는 코드
