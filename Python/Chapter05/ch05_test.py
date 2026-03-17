"""
    제작 시간 : 0317_20:13
    유형 : 과제
    주제 : p352 
    문제 설명 : 
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
    print("# 1번")
    numbers = [1, 2, 3, 4, 5, 6]
    print("::".join(map(str, numbers)))
    print()
    print("# 2번")
    numbers = list(range(1, 10+1))
    print("# 홀수만 출력하기")
    print(list(filter(lambda x:x%2==1, numbers)))
    print()
    print("# 3 이상, 7미만 출력")
    print(list(filter(lambda x: 3<=x<7, numbers)))
    print()
    print("# 제곱해서 50미만 추출하기")
    print(list(filter(lambda x:0<x*x<50, numbers)))
    pass


if __name__ == "__main__":
    main()