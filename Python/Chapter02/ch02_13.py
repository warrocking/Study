"""
    제작 시간 : 0305_16:22
    유형 : 연습
    주제 : 대소문자 바꾸기 : upper()와 lower()
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
    input_str = input("문자열 입력 : ")
    print("대문자로 바꾸기 : ", input_str.upper().strip())  #strip() : 양쪽 공백 제거                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    print("소문자로 바꾸기 : ", input_str.lower().strip()) #strip() : 양쪽 공백 제거
    left_string = "                          left string"
    left_string = left_string.lstrip() # lstrip() : 왼쪽 공백 제거
    print(left_string)
    right_string = "right string                              "
    right_string = right_string.rstrip() # rstrip() : 오른쪽 공백 제거  
    print(right_string)
        #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()