"""
    제작 시간 : 0305_17:15
    유형 : 과제
    주제 : p 152 도전과제 1번
    문제 설명:
    - 구의 부피와 겉넓이 구하기
    - 구의 반지름을 r이라고 할때 
    - 부피 : 4/3 * (파이) * r'3
    - 겉넓이 : 4 * (파이) * r'2
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
    r = input("구의 반지름 입력 : ")
    volume = (4/3) * 3.14 * (float(r) ** 3) # ** : 제곱 연산자
    surfaceArea = 4 * 3.14 * (float(r) ** 2) # ** : 제곱 연산자
    
    print("구의 부피 : ", round(volume, 3))
    print("구의 겉넓이 : ", round(surfaceArea, 3))
    #        입 력

    #        처 리

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()