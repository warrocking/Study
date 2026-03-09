"""
    제작 시간 : 0309_17:17
    유형 : 연습
    주제 : p.214 2번,3번, 4번, 5번
    문제 설명 : 
    - 1. 반복문 내부에 if 조건문의 조건식을 채워서 100 이상의 숫자만 출력하게 만들어 보세요.
    - 2. 짝수 홀수 및 몇자리 숫자인지 판별하는 코드를 작성해보시오.
    - 3. [[],[],[]]안에 숫자 리스트를 넣어라.
    - 4. 리스트 안의 숫자들 중 조건에 맞는 숫자들만 제곱으로 출력하게 만들어보세요.
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
    print("1번 문제")
    numbers = [273, 103, 5, 32, 65, 9, 72, 800, 99]
    print("100 이상 숫자 :", end=" ")
    for number in numbers:
        if number >= 100:
            print(number, end=" ")
    print()
    print("-"*60)
    
    
    
    
    print("2번 문제")
    for number in numbers:
        # 짝수 홀수
        if number % 2 == 0:
            print(f"{number}는 짝수입니다.")
        else:
            print(f"{number}는 홀수입니다.")
        # 자릿수 확인
        if(number/100 >= 1):
            print(f"{number}는 3 자리수입니다.")
        elif(number/10 >= 1):
            print(f"{number}는 2 자리수입니다.")
        else:
            print(f"{number}는 1 자리수입니다.")
        print()    
    print("-"*60)
    
    
    
    
    print("3번 문제")
    output = [[],[],[]]
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for number in numbers:
        output[(number+2)%3].append(number)
    print(output)
    print("-"*60)
    
    
    
    
    print("4번 문제")
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in range(0, len(numbers)//2):
        # j가 1, 3, 5, 7이 나오려면 어떤식을 써야 하는가
        j = 2 * i + 1
        print("i = {}, j = {}".format(i, j))
        numbers[j] = numbers[j] **2
    print(numbers)
    print("-"*60)
    print()
    
    pass


if __name__ == "__main__":
    main()
