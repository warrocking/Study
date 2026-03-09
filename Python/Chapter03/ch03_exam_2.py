"""
    제작 시간 : 0309_12:33
    유형 : 과제
    주제 : p189
    문제 설명 : 나누어 떨어지는 숫자
    - 홀수짝수 구분하는 방법을 응용해서 숫자를 입력하면 그 숫자가 2,3,4,5로 나누어 떨어지는지 확인하는 프로그램 구현.
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
    input_value = input("숫자 입력 : ").strip()
    try:
        number = int(input_value)
    except ValueError:
        print("정수가 아닙니다.")
        return
    
    if number % 2 == 0:
        print("2로 나누어 떨어집니다.")
    elif number % 3 == 0:
        print("3로 나누어 떨어집니다.")
    elif number % 4 == 0:
        print("4로 나누어 떨어집니다.")
    elif number % 5 == 0:
        print("5로 나누어 떨어집니다.")
    else:
        print("2,3,4,5로 나누어 떨어지지 않습니다.")
    
    #        처 리

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()