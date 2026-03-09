"""
    제작 시간 : 0309_12:34
    유형 : 예제
    주제 : 리스트 써보기
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
    list_a = [273, 32, 103, "문자열", True, False]
    
    print(list_a[0])
    print(list_a[1])
    print(list_a[2])
    print(list_a[3])
    print(list_a[1:3])
    
    print("리스트 변경하기")
    list_a[0] = "변경"
    print(list_a)
    #        처 리

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()