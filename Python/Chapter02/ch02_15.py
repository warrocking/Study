"""
    제작 시간 : 0305_17:03
    유형 : 예제
    주제 : split 써보기
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


def main() -> None:
    # 변수 선언 및 초기화
    data = "20.0, 10.0 , 39 , 10.2 , 50"
    data2 = "20.0/10.0/39/10.2/50"
    parsing = data.split(",") # split() : 문자열을 구분자로 나누어 리스트로 반환
    #print(parsing)
    for i in range(len(parsing)):
        parsing[i] = parsing[i].strip() # strip() : 양쪽 공백 제거
        parsing[i] = float(parsing[i]) # float() : 문자열을 실수로 변환
        print(parsing)
        
    parsing2 = data2.split("/") # split() : 문자열을 구분자로 나누어 리스트로 반환
    for i in range(len(parsing2)):
        parsing2[i] = parsing2[i].strip() # strip() : 양쪽 공백 제거
        parsing2[i] = float(parsing2[i]) # float() : 문자열을 실수로 변환
        print(parsing2)    
    
    #        입 력

    #        처 리

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()