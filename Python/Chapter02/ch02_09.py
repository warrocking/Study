"""
    제작 시간 : 0305_15:09
    유형 : 연습
    주제 : 원의 둘레/넓이와 입력 연습
    문제 설명:
    - 상수와 산술 연산, 입력, 출력 흐름 정리
"""

# 기본 모듈


def main() -> None:
    # 변수 선언 및 초기화
    pi = 3.141592653589793
    r = 10

    #        입 력
    print(input("인사말 출력: "))
    print(input("숫자를 입력 : "))
    value_a = int(input("숫자를 입력하세요 : "))
    value_b = int(input("숫자를 입력하세요 : "))

    #        처 리
    circumference = 2 * pi * r
    area = pi * r**2
    sum_ab = value_a + value_b
    diff_ab = value_a - value_b
    prod_ab = value_a * value_b
    div_ab = value_a / value_b
    mod_ab = value_a % value_b

    #        출 력
    print("원주율 = ", pi)
    print("반지름 = ", r)
    print("원의 둘레 : ", circumference)
    print("원의 넓이 : ", area)
    print("두 수의 합 : ", sum_ab)
    print("두 수의 차 : ", diff_ab)
    print("두 수의 곱 : ", prod_ab)
    print("두 수의 나눗셈 : ", div_ab)
    print("두 수의 나머지 : ", mod_ab)


if __name__ == "__main__":
    main()
