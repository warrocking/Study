"""
    제작 시간 : 0316_11:19
    유형 : 과제
    주제 : 
    문제 설명 : 
    - 25*25 or 10 * 10 의 정사각형으로 만들어서 픽셀을 만들어서 간단한 그림을 그리기
    - 팩맨이든 삼각형이든 뭐든 그리기
    - 이후 그 이미지를 뒤집기, 90도 돌리기, 원점 대칭 등의 기능을 넣어서 회전시키고 뒤집어 보기
"""

# 기본 모듈
import sys
import math
import os

def make_pixel(size, type, color=255):# 그림 만들기
    
    for y in range(0, size):
        for x in range(0, size):
            print("w", end=" ")
        print("")
    
    
    pass
def draw_pixel(): # 만든 그림을 출력하기
    
    pass

class _picture_Swing:
    def Turn_Left():#그림 좌로 90도 돌리기
        
        pass
    def Turn_Right():#그림 우로 90도 돌리기
        
        pass
    def Turn_UpDown():#그림 상하 반전
        
        pass
    def Turn_LeftRight():#그림 좌우 반전
        
        pass

def main() -> None:
    
    canvas_size = int(input("캔버스 사이즈를 입력해주세요 : "))
    
    print("{}를 입력하여 {}*{}의 밑바탕이 생성되었습니다.".format(canvas_size, canvas_size, canvas_size))
    
    
    pixel = int(input("원하는 그림을 고르시오.\
        1. 삼각형\
        2. 사각형\
        3. 마름모\
        4. 원\n: "))
    
    if pixel == 1:
        make_pixel(canvas_size, pixel)
        pass
    elif pixel == 2:
        pass
    elif pixel == 3:
        pass
    elif pixel == 4:
        pass
    else:
        pass
    
    pass


if __name__ == "__main__":
    main()