"""
    제작 시간 : 0309_16:21
    유형 : 예제
    주제 : 딕셔너리와 반복문
    문제 설명 : 
    - 딕셔너리 써보기
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
    dict = {
        "name" : "7D 건조망고",
        "type" : "당절임",
        "ingredient" : ["망고", "설탕", "메타중아황산나트륨", "치자황색소"],
        "origin" : "필리핀"
    }
    print(dict)
    print()
    print(dict["name"])
    print(dict["type"])
    print(dict["ingredient"])
    print(dict["origin"])
    print()
    
    # 딕셔너리 추가
    dict["price"] = 5000
    print(dict)
    print()
    
    # 딕셔너리 삭제
    del dict["price"]
    print(dict)
    print()
    
    # KeyError 예외
    try:
        print(dict["price"])
    except KeyError:
        print("존재하지 않는 키에 접근하고 있습니다.")
    print()
        
    # 키 존재 확인
    key = input("> 접근하고자 하는 키 : ")
    if key in dict:
        print(dict[key])
    else:
        print("존재하지 않는 키에 접근하고 있습니다.")
    print()
    
    #        입 력
    
    #        처 리
    
    #        출 력
    
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()