"""
    제작 시간 : 0317_19:19
    유형 : 과제
    주제 : 압축 pdf 안 5장의 p. 314부터 있는 문제 내용 해보기
    문제 설명 : 
    - 1. 반환 값 이용한 3의 배수 합계
    - 2. 반환 값 잉요한 원 면적과 원주
    - 3. 최대 공약수 구하기
    - 4. 소수 구하기
    - 5. 영어 단어 맞주기(딕셔너리 사용)
    - 6. 세 수 중 가장 큰 수 찾기
    - 7. 최소 공배수 구하기
    
"""

# 기본 모듈
import sys

def sum_besu3(n):
    sum = 0
    for i in range(1, n):
        if i%3==0:
            sum = sum + i # sum+=i
    return sum
#-------------------------------
PI = 3.14
def cir_area(radius):
    area = radius * radius * PI
    return area
def cir_circum(radius):
    circum = 2 * PI * radius
    return circum
#-------------------------------
def computeMaxGond(x, y):
    if x>y:
        small = y
    else:
        small = x
    for i in range(1, small+1):
        if((x%i==0) and (y%i==0)):
            result = i
    return result
#-------------------------------
def isPrimeNumber(n):
    prime_yes = True
    for i in range(2, n):
        if n%i==0:
            prime_yes = False
            break
    return prime_yes
#-------------------------------
def matchWord(word , answer):
    if word == answer:
        message = "정답"
    else:
        message = "오답"
    return message
#-------------------------------
def max_Two(i, j):
    if i>j:
        return i
    else:
        return j
def max_Three(x, y, z):
    return max_Two(x, max_Two(y, z))
#-------------------------------
def computeMinGong(x, y):
    if x>y:
        big = x
    else:
        big = y

    while(True):
        if((big%x==0) and (big%y==0)):
            result = big
            break
        big = big + 1
    return result
#-------------------------------



def main() -> None:
    
    # print("# 1번 : 반환 값 이용한 3의 배수 합계")
    # num = int(input("양의 정수를 입력 : "))
    # result = sum_besu3(num)
    # print("1~%d까지의 정수 중 3의 배수의 합 : %d"%(num, result))
    # print()
    # print("# 2번 : 반환 값 이용한 원 면적과 원주")
    # r = float(input("반지름 입력 : "))
    # a = cir_area(r)
    # b = cir_circum(r)
    # print("원의 면적 : %.2f, 원주의 길이 : %.2f"%(a, b))
    # print()
    # print("# 3번 : 최대 공약수 구하기")
    # num1 = int(input("첫 번쨰 수 : "))
    # num2 = int(input("두 번쨰 수 : "))
    # max_gong = computeMaxGond(num1, num2)
    # print("두 수의 최대 공약수 : %d"%max_gong)
    # print()
    # print("# 4번 : 소수 구하기")
    # n = int(input("소수 구하는 범위 : "))
    # print("2~%d까지의 정수 중 소수 : "%n, end=" ")
    # for a in range(2, n+1):
    #     is_prime = isPrimeNumber(a)
    #     if is_prime:
    #         print(a, end=" ")
    # print()
    # print("# 5번 : 영어 단어 맞추기")
    # quiz_dict = {
    #     'apple':'사과', 
    #     'lion':'사자',
    #     'book':'책',
    #     'love':'사랑',
    #     'friend':'친구'
    #     }
    # for i in quiz_dict:
    #     str_ = input(quiz_dict[i]+'에 맞는 영어 단어는? : ')
    #     resutlt = matchWord(str_, i)
    #     print(resutlt)
    # print()
    print("# 6번 : 세 수 중 가장 큰 수 찾기")
    a = int(input("첫번째 수 : "))
    b = int(input("두번째 수 : "))
    c = int(input("세번째 수 : "))
    max_num = max_Three(a, b, c)
    print("{}, {}, {} 중 가장 큰 수 : {}".format(a, b, c, max_num))
    print()
    print("# 7번 : 최소 공배수 구하기")
    num1 = int(input("첫번째 수 : "))
    num2 = int(input("두번째 수 : "))
    min_gong = computeMinGong(num1, num2)
    print("{}와 {}의 최소 공배수 : {}".format(num1, num2, min_gong))
    print()

if __name__ == "__main__":
    main()