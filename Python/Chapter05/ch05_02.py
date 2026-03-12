"""
    제작 시간 : 0312_14:43
    유형 : 예제
    주제 : 5-2 함수의 활용
    문제 설명 : 
    - 핵심 키워드 : 재귀 함수 / 피보나치 수열 / 메모화 / 조기 리턴 
"""

# 기본 모듈
import sys

# 반복문으로 팩토리얼 구하기
def factorial(n):
    output = 1
    for i in range(1, n+1):
        output *= i
    return output

# 재귀로 팩토리얼 구하기
def factorial_recursive(n):
    # n이 0이라면 1을 리턴
    if n == 0:
        return 1
    # n이 0이 아니면 n*(n-1)을 리턴
    return n * factorial_recursive(n-1)

# 재귀 함수로 구현한 피보나치 수열 1
def fibonacci_recursion_01(n):
    if n == 1 or n == 2:
        return 1
    else:
        return fibonacci_recursion_01(n-1) + fibonacci_recursion_01(n-2)

# 재귀 함수로 구현한 피보나치 수열 2
counter =0
def fibonacci_recursion_02(n):
    # 어떤 피보나치 수를 구하는지 출력합니다.
    print("fibonacci({})를 구합니다".format(n))
    global counter  # 안쓰면 UnboundLocalError 생성됨.
    counter += 1
    if n==1 or n==2:
        return 1
    else:
        return fibonacci_recursion_02(n-1) + fibonacci_recursion_02(n-2)

# 메모화로 피보나치 만들기
dictionary_fibonacci= {
    1: 1,
    2: 1
}
def fibonacci_memo(n):
    if n in dictionary_fibonacci:
        # 메모가 되어 있으면 메모된 값을 리턴
        return dictionary_fibonacci[n]
    else:
        # 메모가 되어 있지 않으면 값을 구함
        output = fibonacci_memo(n-1) + fibonacci_memo(n-2)
        dictionary_fibonacci[n] = output
        return output
    


def main() -> None:

    # 반복문으로 팩토리얼 구하기
    print("1! = ", factorial(1))
    print("2! = ", factorial(2))
    print("3! = ", factorial(3))
    print("4! = ", factorial(4))
    print("5! = ", factorial(5))
    print()

    # 재귀 함수로 팩토리얼 구하기
    print("1! = ", factorial_recursive(1))
    print("2! = ", factorial_recursive(2))
    print("3! = ", factorial_recursive(3))
    print("4! = ", factorial_recursive(4))
    print("5! = ", factorial_recursive(5))
    print()
    # 자귀 함수로 구현한 피보나치 수열 1
    print("fibonacci_recursion_01(1) = ", fibonacci_recursion_01(1))
    print("fibonacci_recursion_01(2) = ", fibonacci_recursion_01(2))
    print("fibonacci_recursion_01(3) = ", fibonacci_recursion_01(3))
    print()
    # 자귀 함수로 구현한 피보나치 수열 2
    fibonacci_recursion_02(10)
    print("fibonacci(10) 계산할때 함수를 호출한 횟수는 {}입니다.".format(counter))
    print()
    
    # 메모화로 구현한 피보나치 수열 3
    print("fibonacci_memo(10) = ", fibonacci_memo(10))
    print("fibonacci_memo(20) = ", fibonacci_memo(20))
    print("fibonacci_memo(30) = ", fibonacci_memo(30))

    # 조기 리턴
    
    
    
    
if __name__ == "__main__":
    main()