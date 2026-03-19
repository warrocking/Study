import cv2

# ex03 목표:
# 이미지 2장을 다양한 방식으로 연산해보며
# OpenCV의 기본 연산(add/subtract/absdiff/bitwise)을 익히는 예제입니다.

# 1) 컬러 이미지 읽기
color1 = cv2.imread(r"C:\Study\PYC\Resource\cat.jpg")
color2 = cv2.imread(r"C:\Study\PYC\Resource\BackGround.jpg")

if color1 is None or color2 is None:
    print("이미지 파일을 읽지 못했습니다. 경로를 확인하세요.")
    exit()

# 연산 전에 크기를 동일하게 맞춤
color1 = cv2.resize(color1, (400, 400))
color2 = cv2.resize(color2, (400, 400))

# 단순 덧셈: 픽셀 값이 커져서 전체적으로 밝아질 수 있음
add_image = cv2.add(color1, color2)

# 단순 뺄셈: 두 이미지 차이를 직접 뺌(음수는 0으로 처리)
sub_image = cv2.subtract(color1, color2)

# 2) 그레이스케일로 다시 읽기
# absdiff/bitwise 결과를 보기 쉽게 하기 위해 흑백으로 처리
gray1 = cv2.imread(r"C:\Study\PYC\Resource\cat.jpg", cv2.IMREAD_GRAYSCALE)
gray2 = cv2.imread(r"C:\Study\PYC\Resource\BackGround.jpg", cv2.IMREAD_GRAYSCALE)

if gray1 is None or gray2 is None:
    print("그레이스케일 이미지 읽기에 실패했습니다.")
    exit()

gray1 = cv2.resize(gray1, (400, 400))
gray2 = cv2.resize(gray2, (400, 400))

# absdiff: |A - B| (절대값 차이)
# 배경 비교/움직임 감지의 기초 개념에서 자주 사용
abs_image = cv2.absdiff(gray1, gray2)

# OR: 둘 중 하나라도 켜져 있으면(값이 있으면) 살리는 연산
or_image = cv2.bitwise_or(gray1, gray2)

# AND: 둘 다 켜져 있어야(겹치는 부분) 살리는 연산
and_image = cv2.bitwise_and(gray1, gray2)

# NOT: 이미지 반전(검정<->흰색, 어두움<->밝음)
not_image = cv2.bitwise_not(gray1)

# 결과 출력
cv2.imshow("ADD", add_image)
cv2.imshow("SUBTRACT", sub_image)
cv2.imshow("ABSDIFF", abs_image)
cv2.imshow("BITWISE_OR", or_image)
cv2.imshow("BITWISE_AND", and_image)
cv2.imshow("BITWISE_NOT", not_image)

cv2.waitKey(0)
cv2.destroyAllWindows()
