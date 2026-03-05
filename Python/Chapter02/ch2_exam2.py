"""
    제작 시간 : 0305_17:18
    유형 : 과제
    주제 : p 153 도전문제 2번
    문제 설명:
    - 피타고라스의 정리
    - 피타고라스의 정리는 삼각형의 밑변, 높이, 빗변의 관계를 나타내는 공식
    - a'2 + b'2 = c'2
    - a : 밑변, b : 높이, c : 빗변
    - 밑변과 높이를 입력하면 빗변의 길이를 구하는 프로그램 만들기
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
    bottom = float(input("밑변길이 입력 : "))# 밑변
    height = float(input("높이 입력 : "))# 높이
    
    #        입 력

    #        처 리
    hypotenuse = (float(bottom) ** 2 + float(height) ** 2) ** 0.5 # 빗변 # **0.5 : 제곱근 연산
    #        출 력
    print("빗변의 길이 : ", round(hypotenuse, 3))   
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()