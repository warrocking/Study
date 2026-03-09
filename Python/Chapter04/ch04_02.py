"""
    제작 시간 : 0309_14:22
    유형 : 예제
    주제 : 리스트 연산자
    문제 설명:
    - 리스트 연결하기 : 연결(+) , 반복(*) , len()
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
    list_a = [1, 2, 3]
    list_b = [4, 5, 6]

    print(" # 리스트 ")
    print("list_a : ", list_a)
    print("list_b : ", list_b)
    print()
    
    # 기본 연산자
    print("list_a + list_b : ", list_a + list_b)
    print("list_a * 3 : ", list_a * 3)
    print("list_b * 2 : ", list_b * 2)
    print()
    
    # 함수
    print("len(list_a) : ", len(list_a))
    print("len(list_b) : ", len(list_b))
    print("len(list_a + list_b) : ", len(list_a + list_b))
    print()
    
    #        입 력

    #        처 리

    #        출 력
    pass


if __name__ == "__main__":
    main()