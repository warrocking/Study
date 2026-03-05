"""
    제작 시간 : 0305_15:25
    유형 : 연습
    주제 : 삼각형 넓이 구하기
    문제 설명:
    - 밑변과 높이를 입력받고 넓이 구하기
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
    base = float(input("밑변을 입력 : "))
    height = float(input("높이를 입력 : "))

    #        처 리
    area = 0.5 * base * height
    print("삼각형의 넓이 : ", round(area, 2), "cm²")

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()