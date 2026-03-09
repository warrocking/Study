"""
    제작 시간 : 0309_19:13
    유형 : 예제
    주제 : 연속으로 쓰기
    문제 설명 : 
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


def main() -> None:
    # 변수 선언 및 초기화
    
    
    #        입 력
    number = input("정수 입력 : ")
    last_character = number[-1] # 끝자리를 문자로 받기
    last_number = int(last_character) # 문자로 받은 끝자리를 숫자로 변환
    
    #        처 리
    if     last_number == 0 \
        or last_number == 2 \
        or last_number == 4 \
        or last_number == 6 \
        or last_number == 8 :
        print("짝수입니다.")
    else:
        print("홀수입니다.")
    
    #        출 력
    
    pass


if __name__ == "__main__":
    main()