"""
    제작 시간 : 0312_09:35
    유형 : 예제
    주제 : p 237~ 별그리기
    문제 설명 : 
    - 
"""

# 기본 모듈
import sys

# 추가 모듈 (필요 시 주석 해제)
# import math
# import itertools
# import collections

# 함수 선언/정의 (필요 시 작성)
# def helper():
#     pass


def main() -> None:
    
    
    print("직각 삼각형 출력")
    print()
    output_RightTriangle = ""
    
    for i in range(1, 10):
        for j in range(0, i):
            output_RightTriangle += "*"
        output_RightTriangle += "\n"
    print(output_RightTriangle)
    
    print("코드 스타일을 바꾼 직각 삼각형 출력")
    output = ""
    for i in range(1, 10):
        output += ("*"*i)
        output += "\n"
    print(output)
    
    print("-"*30)
    print()
    
    print("이등변 삼각형 출력")
    print()
    output_IsoscelesTriangle = ""
    for i in range(1, 15):
        # 공백을 뒤집어진 직각삼각형으로 생각해서 그리기
        for j in range(14, i, -1):
            output_IsoscelesTriangle += " "
        
        # 1, 3, 5, ... 로 홀수 갯수로 출력하기
        for j in range(0, 2*i-1):
            output_IsoscelesTriangle += "*"
        output_IsoscelesTriangle += "\n"
    print(output_IsoscelesTriangle)
    
    print("-"*30)
    print()
    
    
    pass


if __name__ == "__main__":
    main()