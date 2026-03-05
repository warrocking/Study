"""
    제작 시간 : 0305_15:45
    유형 : 연습
    주제 : print문을 이용한 변수 표기 차이
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
    input_value = input("값 입력 : ")
    print("입력한 값 : input_value")
    print(f"입력한 값 : {input_value}")
    print("입력한 값 : " + input_value)
    print("입력한 값 : ", input_value)
    print("입력한 값 : %s" %input_value)
    print("입력한 값 : {0}".format(input_value))

    #        입 력

    #        처 리

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()