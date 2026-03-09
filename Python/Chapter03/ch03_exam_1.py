"""
    제작 시간 : 0309_12:27
    유형 : 과제
    주제 : p188
    문제 설명 : 간단한 대화 프로그램
    - 조건문을 사용해서 한 마디 대화를 나눌 수 있는 프로그램.
    - 간단하게 "안녕" 또는 "안녕하세요"를 입력하면 프로그램이 "안녕하세요" 정도의 인사를 할 수 있게 작성.
    - "지금 몇 시야?" 또는 "지금 몇 시예요?"처럼 시간을 물어보면 시간을 응답하게 구현해 보세요.
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
    # input = sys.stdin.readline
    # out_lines: list[str] = []

    #        입 력
    user_input = input("대화 입력 : ")
    if user_input == "안녕" or user_input == "안녕하세요":
        print("> 안녕하세요")
    elif user_input == "지금 몇 시야?" or user_input == "지금 몇 시예요?":
        from datetime import datetime
        now = datetime.now()
        print("> 현재 시간은 {}시 {}분입니다.".format(now.hour, now.minute))
    else:
        print("> ", user_input)
    #        처 리

    #        출 력
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()