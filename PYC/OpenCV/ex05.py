import cv2

# ex05 목표:
# Canny 엣지 검출의 임계값(threshold)을 바꿔가며
# 경계선(윤곽선)이 어떻게 달라지는지 비교하는 예제입니다.

# 그레이스케일로 읽으면 계산이 가볍고, 엣지 결과 해석이 쉬워집니다.
image = cv2.imread(r"C:\Study\PYC\Resource\cat.jpg", cv2.IMREAD_GRAYSCALE)

if image is None:
    print("이미지 파일을 읽지 못했습니다. 경로를 확인하세요.")
    exit()

# cv2.Canny(image, threshold1, threshold2)
# threshold1: 약한 엣지 기준
# threshold2: 강한 엣지 기준
# threshold2가 높아질수록 더 강한 경계만 남는 경향이 있습니다.
canny_edge_50 = cv2.Canny(image, 50.0, 50.0)
canny_edge_100 = cv2.Canny(image, 50.0, 100.0)
canny_edge_150 = cv2.Canny(image, 50.0, 150.0)

# 원본 + 각 조건별 결과를 서로 다른 창에 표시
cv2.imshow("Original", image)
cv2.imshow("Canny_50_50", canny_edge_50)
cv2.imshow("Canny_50_100", canny_edge_100)
cv2.imshow("Canny_50_150", canny_edge_150)

cv2.waitKey(0)
cv2.destroyAllWindows()
