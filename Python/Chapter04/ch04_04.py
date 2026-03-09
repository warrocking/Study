"""
    제작 시간 : 0309_15:19
    유형 : 예제
    주제 : 반복문
    문제 설명 : 
    - 반복문을 다양하게 써보기
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
    list_a = [1, 2, 3, 4, 5]
    for i in list_a:
        print(list_a)
    print()
    
    for charater in "안녕하세요":
        print("-", charater)
    print()
    
    list_of_list = [[1, 2, 3], [4, 5, 6, 7], [8, 9]]
    for items in list_of_list:
        print(items)
    print()
    
    for items in list_of_list:
        for item in items:
            print(item, end = "   ")
        print()
    print()
    
    #        입 력
    #        처 리
    
    #        출 력
    
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()