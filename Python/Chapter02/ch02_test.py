"""
    제작 시간 : 0305_15:18
    유형 : 연습
    주제 : 데이터 입력에 따른 코드 처리
    문제 설명:
    - 반지름 받으면 원의 길이와 넓이를 구하기
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
   
    #        입 력
    r = int(input("반지름을 입력하세요 : "))
    pi = 3.141592653589793
    circumference = 2 * pi * r
    area = pi * r**2

    #        처 리
    print("원의 길이 : ", round(circumference, 2), "cm")
    #print(f"원의 길이 : {circumference : .2f}cm")
    print(f"원의 넓이 : {area : .2f}cm²")
    
    
    
    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()