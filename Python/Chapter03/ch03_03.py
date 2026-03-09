"""
    제작 시간 : 0309_10:10
    유형 : 예제
    주제 : 날짜/시간 활용하기
    문제 설명:
    - 날짜/시간 출력
    - 조건문 활용하여 날짜/시간 출력
"""

# 기본 모듈
import sys
import datetime
# 추가 모듈 (필요 시 주석 해제)
# import math
# import itertools
# import collections

# 함수 선언/정의 (필요 시 작성)
# def helper():
#     pass


def main() -> None:
    # 변수 선언 및 초기화
    now = datetime.datetime.now() # 현재 날짜/시간 가져오기
    print("현재 날짜/시간 : ", now)
    print("\n")
    print("현재 년도 : ", now.year)
    print("현재 월 : ", now.month)
    print("현재 일 : ", now.day)
    print("현재 시 : ", now.hour)
    print("현재 분 : ", now.minute)
    print("현재 초 : ", now.second)
    
    #        입 력
    print("\n")
    #        처 리
    if(now.hour < 12):
        print("현재 시간은 오전입니다.")
    else:
        print("현재 시간은 오후입니다.")
        
    
    print("\n")
    if(3<=now.month<=5):
        print("현재 계절은 봄입니다.")
    elif(6<=now.month<=8):
        print("현재 계절은 여름입니다.")
    elif(9<=now.month<=11):
        print("현재 계절은 가을입니다.")
    else:
        print("현재 계절은 겨울입니다.")
    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()