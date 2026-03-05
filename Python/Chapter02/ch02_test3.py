"""
    제작 시간 : 0305_17:12
    유형 : 연습
    주제 : 합산과 평균
    문제 설명:
    - 국어, 영어, 수학 세 과목의 성적을 입력받아 합계와 평균을 구하는 예이다.
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
    kor = input("국어 성적 입력 : ")
    eng = input("영어 성적 입력 : ")
    math = input("수학 성적 입력 : ")
    
    sum = int(kor) + int(eng) + int(math) # int() : 문자열을 정수로 변환
    avg = sum / 3 # / : 실수 나눗셈
    
    print("합계 : ", sum,)
    print("평균 : ", round(avg, 2))

    #        입 력

    #        처 리

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()