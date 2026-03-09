"""
    제작 시간 : 0309_14:26
    유형 : 예제
    주제 : 리스트에 요소 추가하기
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
    list_a = [1,2,3]
    print("# 리스트 초기화")
    print(list_a)
    print()
    
    #        입 력
    print("# 리스트 뒤에 요소 추가하기")
    list_a.append(4)
    list_a.append(5)
    print(list_a)
    print()
    
    #       리스트 중간에 요소 추가하기
    print("# 리스트 중간에 요소 추가하기")
    list_a.insert(0, 10) # "추가할 목표 리스트".insert("추가할 위치", "추가할 요소")
    print(list_a)
    print()
    
    #       리스트 여러 요소 추가하기
    print("# 리스트 여러 요소 추가하기")
    list_a.extend([20, 30, 40]) # "추가할 목표 리스트".extend("추가할 요소가 담긴 리스트")
    print(list_a)
    print()
    
    #       리스트 요소 삭제하기
    print("# 리스트 요소 삭제하기")
    list_a.remove(10) # "삭제할 목표 리스트".remove("삭제할 요소")
    print(list_a)
    print()
    
    #       리스트 요소 꺼내기
    print("# 리스트 요소 꺼내기")
    list_a.pop() # "꺼낼 목표 리스트".pop()
    print(list_a)
    print()
    
    #       리스트 요소 개수 세기
    print("# 리스트 요소 개수 세기")
    print(list_a.count(20)) # "개수를 셀 목표 리스트".count("세고자 하는 요소")
    print()
    
    #       리스트 정렬하기
    print("# 리스트 정렬하기")
    list_a.sort() # "정렬할 목표 리스트".sort()
    print(list_a)
    print()
    
    #       리스트 순서 뒤집기
    print("# 리스트 순서 뒤집기")
    list_a.reverse() # "뒤집을 목표 리스트".reverse()
    print(list_a)
    print()
    
    #       리스트 요소 모두 지우기
    print("# 리스트 요소 모두 지우기")
    list_a.clear() # "지울 목표 리스트".clear()
    print(list_a)
    print()
    
    #       리스트 내부에 요소가 있는지 확인하기
    print("# 리스트 내부에 요소가 있는지 확인하기")
    print(20 in list_a) # "확인할 요소" in "확인할 리스트"
    print(30 not in list_a) 
    print()
    
    #       리스트 사본 만들기
    print("# 리스트 사본 만들기")   
    list_b = list_a.copy() # "사본을 만들 목표 리스트".copy()
    print(list_b)
    print()
    
    #       리스트 삭제하기
    print("# 리스트 삭제하기")
    del list_a # 리스트 삭제하기
    try:# 삭제된 리스트를 출력하려고 하면 오류가 발생한다.
        print(list_a)
    except NameError:
        print("list_a는 삭제되었습니다.")
    print()
    
    
  

    pass


if __name__ == "__main__":
    main()