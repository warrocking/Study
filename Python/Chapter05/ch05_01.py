"""
    제작 시간 : 0312_12:41
    유형 : 예제
    주제 : 5-1장 함수만들기
    문제 설명 : 
    - 핵심 키워드 : 호출 / 매개변수 / 리턴값 / 가변 매개변수 / 기본 매개변수 / 키워드 매개변수
"""

# 기본 모듈
import sys

# 추가 모듈 (필요 시 주석 해제)
# import math
# import itertools
# import collections

# 함수 선언/정의 (필요 시 작성)
# def helper():

# 코드 구분
def division():
    print("-"*30)
    print("")


# 기본적인 함수
def print_3_times():
    print("안녕하세요")
    print("안녕하세요")
    print("안녕하세요")

# 매개변수가 있는 함수
def print_n_times(value, n):
    for i in range(n):
        print(value)

# 가변 매개변수 함수
def variable_param(n, *values):
    for i in range(n):
        for value in values:
            print(value)
        
        print()

# 기본 매개변수 함수
def default_param(value, n=2):
    for i in range(n):
        print(value)

# 키워드 매개변수 
def param_keyword_01(*value, n=2):
    for i in range(n):
        for values in value:
            print(values)
        print()

# 여러 함수 호출 형태
def param_example(a, b=10, c=100):
    print(a + b + c)

# 자료 없이 리턴하기
def return_only():
    print("A 위치입니다.")
    return 
    print("B 위치입니다.")
    
# 자료와 함께 리턴하기
def return_with_data():
    return 100

# 아무것도 리턴하지 않을 때의 리턴값
def return_none():
    return

# 범위 내부의 정수를 모두 더하는 함수
def sum_all_basic(start, end):
    output = 0
    for i in range(start, end+1):
        output += i
    return output

# 기본 매개변수와 키워드 매개변수를 활용해 범위의 정수를 더하는 함수
def sum_all_with_default(start = 0, end = 100, step = 1):
    output = 0
    for i in range(start, end+1, step):
        output += i
    return output


# 연습문제 - 매개변수로 전달된 값을 모두 곱해서 리턴하는 가변 매개변수 함수를 만들기
def mul(*values):
    total = 1
    for value in values:
        total *= value
    return total


#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
# 키워드 매개변수
def main() -> None:
  
    # 기본적인 함수
    print_3_times()
    division()
    # 매개변수의 기본    
    print_n_times("안녕하세요", 5)
    division()
    
    # 가변 매개변수 함수
    variable_param(3, "안녕하세요", "즐거운", "파이썬 프로그래밍")
    division()
    
    # 기본 매개변수
    default_param("안녕하세요")
    division()
    
    # 키워드 매개변수
    param_keyword_01("안녕하세요", "즐거운", "파이썬 프로그래밍", n=3)
    division()
    
    # 여러 함수 호출 형태
    # 1. 기본형태
    param_example(10, 20, 30)
    # 2. 키워드 매개변수로 모든 매개변수를 지정한 형태
    param_example(a=10, b=100, c=200)
    # 3. 키워드 매개변수로 모든 매개변수를 마구잡이로 지정한 형태
    param_example(c=10, a=100, b=200)
    # 4. 키워드 매개변수로 일부 매개변수만 지정한 상태
    param_example(10, c=200)
    division()
    
    # 자료없이 리턴하기
    return_only()
    division()
    
    # 자료와 함께 리턴하기
    value = return_with_data()
    print(value)
    division()
    
    # 아무것도 리턴하지 않기
    value = return_none()
    print(value)
    division()
    
    # 범위 내부의 정수를 모두 더하는 함수
    print("0 to 100 : ", sum_all_basic(0, 100))
    print("0 to 1000 : ", sum_all_basic(0, 1000))
    print("50 to 100 : ", sum_all_basic(50, 100))
    print("500 to 1000 : ", sum_all_basic(500, 1000))
    division()
    
    # 기본 매개변수와 키워드 매개변수를 활용해 범위의 정수를 더하는 함수
    print("A : ", sum_all_with_default(start=20))
    print("B : ", sum_all_with_default(end=60))
    print("C : ", sum_all_with_default(start=45, end=92))
    print("D : ", sum_all_with_default(start=3, end=87, step=8))
    print("E : ", sum_all_with_default(end =200, step = 6))
    division()
    
    # p.291 연습문제 2
    print(mul(5, 7, 9, 10))
    division()

'''
5가지 키워드로 정리하는 핵심 포인트
- 호출 : 함수를 실행하는 행위를 말한다.
- 매개변수 : 함수의 괄호 내부에 넣는것을 의미
- 리턴 값 : 함수의 최종적인 결과를 의미
- 가변 매개변수 : 함수는 매개변수를 원하는 만큼 받을 수 있는 함수
- 기본 매개변수 : 매개변수에 아무것도 넣지 않아도 들어가는 값
'''




if __name__ == "__main__":
    main()
'''

그 코드는 “이 파일을 직접 실행했을 때만 main()을 호출하라” 는 의미입니다.

__name__은 파이썬이 자동으로 넣는 변수입니다.
이 파일을 직접 실행하면 __name__ == "__main__"가 됩니다.
다른 파일에서 import되면 __name__은 파일 이름이 됩니다.
그래서 직접 실행할 때만 main() 실행되고, import될 때는 실행되지 않습니다.
요약:

실행 파일일 때만 동작하게 하는 안전장치입니다.

'''
