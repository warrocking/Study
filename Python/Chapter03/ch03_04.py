"""
    제작 시간 : 0309_10:30
    유형 : 연습
    주제 : 조건문 활용 문제
    문제 설명:
    - 입력을 받고, 해당 입력에 따라 짝수 홀수 구분하기
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
    value_str = input("값 입력 : ").strip()
    # strip 역할 : 양쪽 공백 제거, 입력값이 "  10  "인 경우, strip()을 사용하면 "10"이 됨.

    # 정수 판별
    # int() 변환이 가능하면 정수로 인정
    # 불가능하면 valueError 가 발생하고 '정수가 아닙니다' 출력.
    # try-except 구문을 사용하여 예외 처리
    try:
        value = int(value_str)
    except ValueError:
        print("정수가 아닙니다.")
        return

    #        처 리
    if value % 2 == 0:
        print("짝수입니다.")
    else:
        print("홀수입니다.")

    # 다른 표현
    last_number = int(value_str[-1]) # 입력값의 마지막 문자(숫자)를 정수로 변환
    if last_number % 2 == 0:
        print("짝수입니다.")
    else:
        print("홀수입니다.")
    
    if last_number in "02468": # 입력값의 마지막 문자가 짝수인 경우
        #if last_number in ["0", "2", "4", "6", "8"]:
        print("짝수입니다.")
    else:        print("홀수입니다.")
    #        출 력
    # sys.stdout.write("\n".join(out_lines))
    pass


if __name__ == "__main__":
    main()
