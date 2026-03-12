"""
    제작 시간 : 0312_09:32
    유형 : 예제
    주제 : p234 for 반복문과 범위
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
    # 변수 선언 및 초기화
    
    for i in range(5):
        print(str(i) + "= 반복 변수")
    print()
    
    for i in range(5, 10):
        print(str(i)+ " = 반복 변수")
    print()
    
    for i in range(0, 10, 3):
        print(str(i) + " = 반복 변수")
    print()
    
    array = [273, 32, 103, 57, 52]

    for i in range(len(array)):
        print("{}번째 반복 : {}".format(i, array[i]))
    print()
    
    print("for문 역순으로 출력하기")
    for i in range(4, 0 -1 , -1):
        print("현재 반복 변수 : {}".format(i))
    print()
    
    for i in reversed(range(5)):
        print("현재 반복 변수 : {}".format(i))
    print();    
    pass


if __name__ == "__main__":
    main()