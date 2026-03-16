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

# 조기 리턴으로 피보나치 만글기
def fibonacci_early_return(n):
    if n in dictionary_fibonacci:
        return dictionary_fibonacci[n]
    output = fibonacci_early_return(n-1) + fibonacci_early_return(n-2)
    dictionary_fibonacci[n] = output
    return output

# 리스트 평탄화하기 _ 1
def list_flatten_1(data):
    output = []
    for item in data:
        if type(item) == list:
            output += list_flatten_1(item)
        else:
            output.append(item)
    return output

# 리스트 평탄화하기 _ 2
def list_flatten_2(data):
    output = []
    for item in data:
        if type(item) == list:
            output += list_flatten_2(item)
        else:
            output.append(item)
    return output

# p.315 연습문제
# - 식당에 여러 개의 테이블이 있다. 1명만 앉는 경우가 없게, 인원수를 나누는 패턴을 구하고,
#   10명이 앉는 경우의 수를 구하라.
# - ex) 6명의 경우 -> 2+2+2 / 2+4 / 3+3 / 6 -> 4가지
MIN_PEOPLE_PER_TABLE = 2
MAX_PEOPLE_PER_TABLE = 10


def algorizum(n, m=MIN_PEOPLE_PER_TABLE, show_patterns=False):
    # show_patterns: False/0이면 경우의 수만 반환, True/1이면 패턴 출력 + 경우의 수 반환
    show_patterns = bool(show_patterns)

    memo = {}

    def count_case(remaining, min_table_size):
        key = (remaining, min_table_size)
        if key in memo:
            return memo[key]

        if remaining == 0:
            return 1

        if remaining < min_table_size:
            return 0

        if min_table_size > MAX_PEOPLE_PER_TABLE:
            return 0

        use_current = count_case(remaining - min_table_size, min_table_size)
        skip_current = count_case(remaining, min_table_size + 1)
        memo[key] = use_current + skip_current
        return memo[key]

    def collect_patterns(remaining, min_table_size, current, out):
        if remaining == 0:
            out.append(current[:])
            return

        if remaining < min_table_size:
            return

        if min_table_size > MAX_PEOPLE_PER_TABLE:
            return

        # 현재 크기(min_table_size)를 사용
        collect_patterns(
            remaining - min_table_size,
            min_table_size,
            current + [min_table_size],
            out,
        )
        # 현재 크기를 건너뛰고 다음 크기로 이동
        collect_patterns(remaining, min_table_size + 1, current, out)

    total = count_case(n, m)

    if show_patterns:
        patterns = []
        collect_patterns(n, m, [], patterns)
        for pattern in patterns:
            print(" + ".join(str(x) for x in pattern))

    return total


#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

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
    print("fibonacci_early_return(10) = ", fibonacci_early_return(10))
    print("fibonacci_early_return(20) = ", fibonacci_early_return(20))
    print("fibonacci_early_return(30) = ", fibonacci_early_return(30))
    print()

    # 리스트 평탄화하기_1
    example = [[1, 2, 3], [4, [5, 6]], 7, [8, 9]]
    print("평탄화하기 : {} -> {}".format(example, list_flatten_1(example)))
    print()
    
    #리스트 평탄화하기_2
    example = [[1, 2, 3], [4, [5, 6]], 7, [8, 9]]
    print("평탄화하기 : {} -> {}".format(example, list_flatten_2(example)))
    print()

    # p.315 연습문제 
    print("p.315 연습문제")
    print("6명 패턴:")
    print("6명 경우의 수 :", algorizum(6, MIN_PEOPLE_PER_TABLE, True))
    print("10명 경우의 수 :", algorizum(10, MIN_PEOPLE_PER_TABLE, False))
    print("100명 경우의 수 :", algorizum(100, MIN_PEOPLE_PER_TABLE, 1))
    
    """
        - 3가지 키워드로 정리하는 핵심 포인트
         - 재귀 함수 : 내부에서 자기자신을 호출하는 함수
         - 메모화 : 한 번 계산한 값을 저장한 후, 이후에 다시 계산하지 않고 저장된 값을 활용하는 테크닉
         - 조기 리턴 : 함수의 흐름 중간에 return 키워드를 사용해서 코드 들여쓰기를 줄이는 등의 효과를 가져오는 테크닉
    """
    

    
if __name__ == "__main__":
    main()
