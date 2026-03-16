"""
    제작 시간 : 0313_14:05
    유형 : 연습
    주제 : 문제 풀이
    문제 설명 : 
    - 1. 반환값을 이용한 원 면적과 원주
    - 2. 두수를 입력 받고 최대 공약수 구하기
    - 3. 소수 구하기
"""

# 기본 모듈
import sys
PI = 3.14
# 추가 모듈 (필요 시 주석 해제)
# import math
# import itertools
# import collections

# 함수 선언/정의 (필요 시 작성)
# 반지름을 이용한 원의 면적과 원의 길이
def cir_area(radius):
    area = radius * radius * PI
    return area
def cir_circum(radius):
    circum = 2*PI*radius
    return circum
# 최대 공약수 구하기
def computeMaxGong(x, y):
    if x>y:
        small = y
    else:
        small = x
    for i in range(1, small+1):
        if((x%i==0) and (y%i==0)):
            result = i
    return result
# 소수 구하기
def isPrime_sqrt(n):
    list_Prime = []
    if n < 2:
        return list_Prime
    for y in range(2, n + 1):
        prime_flag = True
        for x in range(2, int(y ** 0.5) + 1):
            if y % x == 0:
                prime_flag = False
                break
        if prime_flag:
            list_Prime.append(y)
    return list_Prime

# 소수 구하기(비교용: 2~n-1 완전 탐색)
def isPrime_full_scan(n):
    list_Prime = []
    if n < 2:
        return list_Prime
    for y in range(2, n + 1):
        prime_flag = True
        for x in range(2, y):
            # 즉, 12까지 넣고 y=7이라 할때 자기 자신만 나눌 수 있을때만 append하고, 
            # 나눠지는게 있다면 소수가 아니니 없애기
            if y % x == 0:
                prime_flag = False
                break
        if prime_flag:
            list_Prime.append(y)
    return list_Prime

def main() -> None:
    # 변수 선언 및 초기화
    print("1번 문제 : 반환 값을 이용한 원 면적과 원주")
    r = float(input("반지름을 입력 : "))
    a = cir_circum(r)
    b = cir_area(r)
    print("원의 면적 : %.2f\n, 원주의 길이 : %.2f"%(a,b))
    print("-"*60)
    print("2번 문제 : 두수를 입력 받고 최대 공약수 구하기")
    x = int(input("첫번째 수 : "))
    y = int(input("두번째 수 : "))
    result = computeMaxGong(x, y)
    print("두 수의 최대 공약수 : %d"%result)
    print("-"*60)
    print("3번 문제 : 소수 구하기")
    n = int(input("1부터 소수를 구할 범위를 적어주시오 : "))
    prime_sqrt = isPrime_sqrt(n)
    prime_full = isPrime_full_scan(n)
    print("[sqrt 방식] {}까지의 모든 소수는 {}이다".format(n, prime_sqrt))
    print("[2~n-1 방식] {}까지의 모든 소수는 {}이다".format(n, prime_full))
    print("두 방식 결과가 같은가? :", prime_sqrt == prime_full)
    print("-"*60)






if __name__ == "__main__":
    main()
