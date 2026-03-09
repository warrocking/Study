"""
    제작 시간 : 0309_09:44
    유형 : 예제
    주제 : 양수 음수 판별로 Boolen 출력
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


    #        입 력
    input_value = input("정수 입력 : ")
    
    #        처 리
    if(int(input_value)>=0):
        print("양수입니다.")
    elif(int(input_value)<0):
        print("음수입니다.")
    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()