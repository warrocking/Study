"""
    제작 시간 : 0305_16:35
    유형 : 예제
    주제 : 문자열의 구성파악하기 : isOO()
    문제 설명:
    - isalnum() : 문자열이 영문자 또는 숫자로만 구성되어 있는지 확인
    - isalpha() : 문자열이 영문자로만 구성되어 있는지 확인
    - isidentifier() : 문자열이 식별자로 사용할 수 있는지 확인
    - isdecimal() : 문자열이 숫자로만 구성되어 있는지 확인
    - isdigit() : 문자열이 숫자로만 구성되어 있는지 확인
    - isspace() : 문자열이 공백으로만 구성되어 있는지 확인
    - islower() : 문자열이 소문자로만 구성되어 있는지 확인
    - isupper() : 문자열이 대문자로만 구성되어 있는지 확인
    
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
    print("\n")
    print("-" * 50)
    print("\n")

def main() -> None:
   
    line()
    print("isalnum() : 문자열이 영문자 또는 숫자로만 구성되어 있는지 확인")
    print("\'TrainA10\'isalnum -> ", "TrainA10".isalnum())
    print("\'10\'isalnum -> ", "10".isalnum())
    
    line()
    print("isdigit() : 문자열이 숫자로만 구성되어 있는지 확인")
    print("\'TrainA10\'isdigit -> ", "TrainA10".isdigit())
    print("\'10\'isdigit -> ", "10".isdigit())
    
    line()
    print("isalpha() : 문자열이 영문자로만 구성되어 있는지 확인")
    print("\'TrainA10\'isalpha -> ", "TrainA10".isalpha())
    print("\'Train\'isalpha -> ", "Train".isalpha())
    
    line()
    print("isidentifier() : 문자열이 식별자로 사용할 수 있는지 확인")
    print("\'TrainA10\'isidentifier -> ", "TrainA10".isidentifier())
    print("\'10Train\'isidentifier -> ", "10Train".isidentifier())
    
    line()
    print("isdecimal() : 문자열이 숫자로만 구성되어 있는지 확인")
    print("\'TrainA10\'isdecimal -> ", "TrainA10".isdecimal())
    print("\'10\'isdecimal -> ", "10".isdecimal())
    
    line()
    print("isupper() : 문자열이 대문자로만 구성되어 있는지 확인")
    print("\'TrainA10\'isupper -> ", "TrainA10".isupper())
    print("\'TRAIN\'isupper -> ", "TRAIN".isupper())
    
    line()
    print("islower() : 문자열이 소문자로만 구성되어 있는지 확인")
    print("\'TrainA10\'islower -> ", "TrainA10".islower())
    print("\'train\'islower -> ", "train".islower())
    
    line()
    print("find() : 문자열에서 특정 문자열의 위치를 반환")
    print("\'TrainA10\'find('A') -> ", "TrainA10".find("A"))
    print("\'TrainA10\'find('B') -> ", "TrainA10".find("B"))
    
    line()
    print("rfind() : 문자열에서 특정 문자열의 위치를 반환 (오른쪽부터 검색)")
    print("\'TrainA10\'rfind('A') -> ", "TrainA10".rfind("A"))
    print("\'TrainA10\'rfind('B') -> ", "TrainA10".rfind("B"))
   
    
    
    
    
    
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()