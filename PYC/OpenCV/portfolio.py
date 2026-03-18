"""
    제작 시간 : 0318_15:29
    유형 : 과제
    주제 : OpenCV로 간단한 게임 만들기
    문제 설명 : 
    - 1. 카메라 인식
    - 2. 카메라 및 코드 세팅
    - 3. 캠 화면 켜짐
    - 4. 캠 화면에 목록이 뜸.
    - 5. 목록을 손가락으로 건드리면서 생기는 변화량이 몇초 누적하면 그 항목을 실행
    - 6. 항목은 "1. 게임 시작 2. 카메라 변경(흑백 카메라, 필터 onoff 등) 3. 프로그램 종료"
    - 7. 게임 시작 하면 화면에 다양한 이미지가 뜨며 이미지가 이동하거나, 가먼히 있음.
    - 8. 이미지별로 손으로 건드리면 이미지가 사라짐.
    - 9. 없어지는 이미지 별로 게임 점수가 누적됨.
    - 10. 시스템 시간을 좌상단에 표시하여 1분동안 타이머를 진행함.
    - 11. 타이머 1분 후 점수 표시 후, 10초 후 3~4번 쪽으로 이동
"""

import sys
import cv2
import os
import time

class Object_Pooling:
    def __init__(self):
        super().__init__()
        



def capFilter(object, ):
    
    pass


def main() -> None:
    
    # 캠 지정해주기
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("WebCam is not define")
        return 0
    
    
    
    
    # 
    
    pass


if __name__ == "__main__":
    main()
    pass