"""
    제작 시간 : 0305_16:07
    유형 : 연습
    주제 : format() 함수의 다양한 기능
    문제 설명:
    - 
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

def line():
    print("-" * 30)

def main() -> None:
    
    # 정수
    output_a = "{:d}".format(52)
    
    # 특정 칸에 출력하기
    output_b = "{:5f}".format(52) # 5칸 확보 후 출력
    output_c = "{:10d}".format(52) # 10칸 확보 후 출력
    
    # 빈칸을 0 으로 채우기
    output_d = "{:05d}".format(52) # 5칸 확보 후 빈칸을 0으로 채우기
    output_e = "{:05d}".format(-52) # 5칸 확보 후 빈칸을 0으로 채우기
    
    print("#기본")
    print(output_a)
    line()
    print("#특정 칸에 출력하기")
    print(output_b)
    print(output_c)
    line()
    print("#빈칸을 0으로 채우기")
    print(output_d)
    print(output_e)
    line()

    # 기호와 함께 출력하기
    output_f = "{:+d}".format(52) # 양수
    output_g = "{:+d}".format(-52) # 음수
    output_h = "{: d}".format(52) # 양수 : 기호 부분 공백
    output_i = "{: d}".format(-52) # 음수 : 기호 부분 공백
    
    print("#기호와 함께 출력하기")
    print(output_f)
    print(output_g)
    print(output_h)
    print(output_i)
    line()
    # 조합하기
    output_h = "{:+5d}".format(52) # 기호를 뒤로 밀기 : 양수
    output_i = "{:+5d}".format(-52) # 기호를 뒤로 밀기 : 음수
    output_j = "{:=+5d}".format(52) # 기호를 앞으로 밀기 : 양수
    output_k = "{:=+5d}".format(-52) # 기호를 앞으로 밀기 : 음수
    output_l = "{:+05d}".format(52) # 0으로 채우기 : 양수
    output_m = "{:+05d}".format(-52) # 0으로 채우기 : 음수
    
    print("#조합하기")
    print(output_h)
    print(output_i)
    print(output_j)
    print(output_k)
    print(output_l)
    print(output_m)
    line()
    
    pass


if __name__ == "__main__":
    main()