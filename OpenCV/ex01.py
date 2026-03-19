import cv2
import numpy as np

# ex01 목표:
# 고양이 이미지와 배경 이미지를 "가중치"로 섞어서
# 점점 바뀌는(페이드 인/아웃) 효과를 보여주는 예제입니다.

# 1) 이미지 파일 읽기
# cv2.imread()는 파일을 읽어서 numpy 배열(이미지 데이터)로 반환합니다.
image1 = cv2.imread(r"C:\Study\PYC\Resource\cat.jpg")
image2 = cv2.imread(r"C:\Study\PYC\Resource\BackGround.jpg")

# 파일 경로가 틀리면 None이 반환되므로, 초기에 확인하는 습관이 중요합니다.
if image1 is None or image2 is None:
    print("이미지 파일을 읽지 못했습니다. 경로를 확인하세요.")
    exit()

# 2) 두 이미지를 같은 크기로 맞춤
# 이미지 연산(addWeighted)은 두 이미지의 크기가 같아야 안전하게 처리됩니다.
image1 = cv2.resize(image1, (400, 400))
image2 = cv2.resize(image2, (400, 400))

# 3) 가중치 블렌딩(혼합) 반복
# np.arange(0.1, 1.0, 0.1) -> 0.1, 0.2, ..., 0.9
for alpha in np.arange(0.1, 1.0, 0.1):
    # beta는 나머지 비율(1 - alpha)
    beta = 1.0 - alpha

    # cv2.addWeighted(A, a, B, b, g)
    # 결과 = A*a + B*b + g
    # g(감마)는 전체 밝기를 조금 올리거나 내릴 때 사용합니다.
    blended = cv2.addWeighted(image1, alpha, image2, beta, 1.0)

    # 혼합 결과를 같은 창 이름에 계속 표시하면 영상처럼 보입니다.
    cv2.imshow("Blend Cat + Background", blended)
    cv2.waitKey(500)  # 500ms(0.5초)씩 대기

# 모든 OpenCV 창 닫기
cv2.destroyAllWindows()
