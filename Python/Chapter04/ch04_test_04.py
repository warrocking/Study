"""
    제작 시간 : 0312_11:52
    유형 : 연습
    주제 : p267 연습문제 2번
    문제 설명 : 
    - 1~100까지의 숫자를 2진수로 변환해서 '0이 "하나"만 포함된 숫자'를 찾아서 그 숫자들의 합을 구해라.
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
   
    # 변수 지정 및 초기화
    output = []
    combine_list = []
    sum =0
    
    # 함수 처리
    for i in range(1, 101):
        binary = bin(i)[2:]        # "0b" 제거 → "1011"
        combine_list.append(binary)
        print("{} : {}".format(i, combine_list[i-1]))
        
    for j in range(0, len(combine_list)):
        if combine_list[j].count("0") == 1:
            output.append(combine_list[j])
            
    for k in range(0, len(output)):
        print(output[k])   
    
    for l in range(0, len(output)):
        sum += int(output[l], 2)
    
    # 최종 출력
    print("합계 : {}".format(sum))
    print()
    
    pass


if __name__ == "__main__":
    main()