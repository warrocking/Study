"""
    제작 시간 : 0309_11:17
    유형 : 연습
    주제 : 다이어트 유무 판정
    문제 설명:
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
    # input = sys.stdin.readline
    # out_lines: list[str] = []

    #        입 력
    height = input("키 입력 : ")
    weight = input("몸무게 입력 : ")
    s = (int(height)-100) * 0.9
    if int(weight) > s:
        print("과체중입니다.")
    elif int(weight) < s:
        print("저체중입니다.")
    else:
        print("표준입니다.")
        
    
    
    #        처 리

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()