"""
    제작 시간 : 0309_12:24
    유형 : 연습
    주제 : p187
    문제 설명:
    - 사용자에게 태어난 연도를 입력받아 띠를 출력하는 프로그램 작성.
    - 작성 시 입력 받은 연도를 12로 나눈 나머지를 사용.
    - 나머지가 0~11일떄 각각 '자축인묘 진사오미 신유술해'를 표시한다.
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
    birth_year = input("태어난 연도 입력 : ")
    try:
        birth_year_int = int(birth_year)
    except ValueError:
        print("정수가 아닙니다.")
        return
    remainder = birth_year_int % 12
    if remainder == 0:
        print("원숭이띠")
    elif remainder == 1:
        print("닭띠")
    elif remainder == 2:
        print("개띠") 
    elif remainder == 3:
        print("돼지띠")
    elif remainder == 4:
        print("쥐띠")
    elif remainder == 5:
        print("소띠")
    elif remainder == 6:
        print("범띠")
    elif remainder == 7:
        print("토끼띠")
    elif remainder == 8:
        print("용띠")
    elif remainder == 9:
        print("뱀띠")
    elif remainder == 10:
        print("말띠")
    elif remainder == 11:
        print("양띠")

    #        처 리

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()