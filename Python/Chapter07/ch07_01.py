"""
    제작 시간 : 0317_11:55
    유형 : 예제
    주제 : 표준 모듈
    문제 설명 : 
    - 핵심 키워드 : 표준 모듈 , import 구문, from 구문 , as 키워드
"""

# 기본 모듈
import sys

# 추가 모듈 (필요 시 주석 해제)

# import itertools
# import collections

# 함수 선언/정의 (필요 시 작성)
# def helper():
#     pass
def math_print():
    import math
    print("math.sin(1) : ", math.sin(1))
    print("math.tan(1) : ", math.tan(1))
    print("math cos(1) : ", math.cos(1))
    print("math.floor(2.5) : ", math.floor(2.5))#내림
    print("math.ceil(2.5) : ", math.ceil(2.5))#올림
    print("반올림 2.51 : ", round(2.51))
    
### 만약 앞에 math를 붙이기 싫다면, 모든 기능을 가져오는 것이 목적이라면, * 기호를 사용함
### * 기호는 컴퓨터에서 '모든 것'을 의미함.
### from math import *    

def math_as():
    import math as m
    print("math.sin(1) : ", m.sin(1))
    print("math.tan(1) : ", m.tan(1))
    print("math cos(1) : ", m.cos(1))
    print("math.floor(2.5) : ", m.floor(2.5))#내림
    print("math.ceil(2.5) : ", m.ceil(2.5))#올림
    print("반올림 2.51 : ", round(2.51))
    
def module_random():
    import random as R
    print("# random 모듈")
    
    # random() : 0.0 <= x < 1.0 사이의 float를 리턴
    print("- random() : ", R.random())
    
    # uniform(min , max) : 지정한 범위 사잉의 float를 리턴
    print("- uniform(10, 20) : ", R.uniform(10, 20))
    
    # randrange() : 지정한 범위의 int를 리턴
    # - randrange(max) : 0 ~ max 사이 값을 리턴
    # - randrange(min, max) : min부터 max 사이의 값을 리턴
    print("- randrange(10) : ", R.randrange(10))
    
    # choice(list) : 리스트 내부에 있는 요소를 랜덤하게 선택
    print("- choice([1, 2, 3, 4, 5])")

def main() -> None:
    

    math_as()
    
    pass


if __name__ == "__main__":
    main()