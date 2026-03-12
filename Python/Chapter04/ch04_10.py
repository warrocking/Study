"""
    제작 시간 : 0312_11:29
    유형 : 예제
    주제 : 시간 코드 다루기
    문제 설명 : 
    - 
"""

# 기본 모듈
import sys
import time
# 추가 모듈 (필요 시 주석 해제)
# import math
# import itertools
# import collections

# 함수 선언/정의 (필요 시 작성)
# def helper():
#     pass


def main() -> None:
    # 변수 선언 및 초기화
    # input = sys.stdin.readline
    # out_lines: list[str] = []
    start_time = time.time()
    #time.sleep(2)#2초 잠들기
    sum = 0
    for i in range(0, 100000001):#1억까지 2.5초 내외
        sum += i
    end_time = time.time()
    print("1부터 100000000까지의 합은 : {}".format(sum))
    print("로딩 시간 : {}".format(end_time-start_time))
    #        입 력
    
    #        처 리
    
    #        출 력
    
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()