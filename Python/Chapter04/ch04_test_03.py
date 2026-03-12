"""
    제작 시간 : 0312_10:22
    유형 : 연습
    주제 : p.248 연습문제 2, 3, 4번
    문제 설명 : 
    - 2. 키와 값으로 이루어진 각 리스트를 조합해 하나의 딕셔너리 만들기
    - 3. 1부터 숫자를 하나씩 증가시키면서 더하는 경우 , 몇을 더할 떄 1,000을 넘는지, 그때의 값은 얼마인지 출력하기.
    - 4. 1부터 100까지의 수 있을때, 1*99, 2*98, 3*97, 4*96 ... 98*2, 99*1라는 규칙에서 최대의 경우는 어떤 숫자의 조합인지 출력.
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

    key_list = ["name", "hp", "mp", "level"]
    value_list = ["기사", 200, 30, 5]
    character = {}
    #
    for i in range(len(key_list)):
        character[key_list[i]] = value_list[i]
    #
    print(character)
    
    print()
    
    limit = 10000
    i=1
    sum_value = 0
    while sum_value <= limit:
        sum_value += i
        i += 1
    print("{}를 더할 때 {}를 넘으면 그때의 값은 {}입니다.".format(i-1, limit, sum_value))
    
    print()
    
    max_value = 0
    a = 0
    b=0
    
    for i in range(1, 101):
        j = 100 - i
        if i * j > max_value:
            max_value = i * j
            a = i
            b = j
    print("최대가 되는 경우: {} * {} = {}".format(a, b, max_value))
    
    
    
    
    
    
    
    
    
    
    pass


if __name__ == "__main__":
    main()