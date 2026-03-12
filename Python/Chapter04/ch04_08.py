"""
    제작 시간 : 0312_09:51
    유형 : 예제
    주제 : p241 while문 써버기
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
    
    i = 0
    print("while문 써보기")
    while i<10:
        print("{}번쨰 반복입니다.".format(i))
        i+=1
    print()


    print("해당하는 값 모두 제거하기")    
    list_test = [1, 2, 1, 2]
    value = 2
    print("list = {}", list_test)
    while value in list_test:
        list_test.remove(value)
    print(list_test)
    
    
    print("5초 동안 반복하기")
    
    import time
    number = 0
    target_tick = time.time() + 5
    while time.time() < target_tick:
        number += 1
    print("5초 동안 {}번 반복했습니다.".format(number))
    print()
    print("while문/break문/continue문 써보기")
    i=0
    while True:
        print("{}번째 반복입니다.".format(i))
        i+=1
        input_text = input("> 종료하시겠습니까?(y/n) : ")
        if input_text in ["y", "Y"]:
            print("반복을 종료합니다.")
            break
    print()
    
    numbers = [5, 15, 6, 20, 7, 25]
    for number in numbers:
        if number < 10:
            continue
        print(number)
    print()
    
    
    pass



if __name__ == "__main__":
    main()