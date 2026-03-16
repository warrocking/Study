"""
    제작 시간 : 0313_12:10
    유형 : 과제
    주제 : 랜덤 시스템 라이브러리 구현
    문제 설명 : 
    - 라이브러리 코드를 구현하기
    - 어떤 곳에서도 사용가능하도록 구현을 목표함.
    - 뽑기 갯수는 기본 매개변수
    - 숫자범위 / 겹치기 가능 or 불가능 / 몇번 반복 후 값 출력할건지 
    / 기본1개에서 몇개까지 동시에 출력할건지 / 뽑기 후에 결과를 다음 뽑기에 넣을 건지 말건지 / 몇번 반복할건지
    등등을 가변 변수로 설정
    
    
"""

# 기본 모듈
import sys
import math
import random
# import itertools
# import collections

def Random(count, range_min = 1, range_max = 100, overlap = False, sort_result = True, NonNumber = []):
    # count = 뽑기 갯수
    # range_min = 랜덤 범위 시작값
    # range_max = 랜덤 범위 최댓값-1
    # overlap = 중복 뽑기 가능, 불가능 판별
    # sort_result = 정렬해서 출력할건지 안할건지
    # NonNumber = 뽑기 중 제외할 요소들
    
    
    list_Random = []
    i=0
    while(i!=count):# 뽑기 갯수 다 채울때까지 뽑기
        random_Num = random.randrange(range_min, range_max) #뽑기 범위 지정
        if(random_Num not in NonNumber):#뽑기 중 제외 범위의 요소가 뽑히면
            if(overlap == True):#중복 허용
                list_Random.append(random_Num)
                i+=1
            else:#중복 비허용
                if(list_Random.count(random_Num)==0):
                    list_Random.append(random_Num)
                    i+=1
    if(sort_result):
        list_Random.sort()# 리스트를 숫자별로 정렬
    return list_Random    

def Random_NonNumber():
    
    pass
    

# def main() -> None:
    
#     for i in range(0,10):
#         print(Random(6))
    
#     pass


# if __name__ == "__main__":
#     main()