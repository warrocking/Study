"""
    제작 시간 : 0310_12:25
    유형 : 과제
    주제 : p268 4장 도전과제
    문제 설명 : 
    - 1. 숫자의 종류 
        - 리스트에서 몇가지 종류의 숫자가 사용되었는지 구하는 프로그램 작성. 
        - 예시로, 1,2,3,4,가 사용되었다면 4개가 사용되었다고 출력해야한다.
    - 2. 염기의 개수 
        - 우리 몸은 DNA라는 설계도에 의해서 만들어진다. 
        - DNA는 A(아데닌), T(티민), G(구아닌), C(사이토닌)이라는 4가지 요소로 구성되는 리스트라고 볼 수 있다.
        ex) ctacaatgtca....
        - 염기 서열을 입력했을 때 각각의 염기가 몇 개 포함되어 있는지 세는 프로그램을 구현해라.
    - 3. 염기 코돈 개수
        - 염기 서열은 일반적으로 3개씩 묶여서 하나의 의미를 나타낸다. 염기 서열을 3개씩 묶여있는 것을 '코돈'이라 부른다.
        - 염기 서열을 입력했을 때, 어떤 코돈이 몇 개 존재하는지 다음과 같이 출력하는 프로그램을 구현해라.
        - 단, 다음과 같이 5글자를 입력하면 분석했을 때 마지막 염기 서열리 3개로 조합되지 못한다. 
            ex) ctaca
        - 위와 같이 남은 염기 서열은 결과에서 무시한다.
    - 4. 2차원 리스트 평탄화
        - 다음과 같이 리스트가 중첩되어 있을 때 중첩을 제거하는 처리를 '리스트 평탄화(list flatten)'라고 한다.
        - ex) [1, 2, [3, 4, [5, 6]], 7, [8, 9]] -> [1, 2, 3, 4, 5, 6, 7, 8, 9]
        - 위와 같이 중첩리스트가 입력됬을 때, 다음과 평탄화를 진행하는 코드르 작성해라.
        - 주의, 리스트 평탄화를 할 때는 요소가 일반 요소인지 리스트인지 확인하는 처리가 필요. 'type()'함수 사용 필요.
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
    print("1번 문제")
    print("-"*60)
    member = [1, 4, 3, 2, 4, 2, 4, 1, 1, 2, 2, 1, 3 ,4, 2, 2, 5]
    # while문으로 각 숫자의 개수를 센다(리스트 내용이 바뀌어도 동작).
    counts = {}  # 숫자별 개수를 저장하는 딕셔너리
    i = 0  # 리스트 인덱스 시작값
    while i < len(member):  # 리스트 길이만큼 반복
        num = member[i]  # 현재 위치의 숫자 꺼내기
        # num이 이미 counts에 있으면 1 증가, 없으면 처음 등장으로 1 저장
        if num in counts:
            counts[num] += 1
        else:#처음 저장이라면 최초의 1 지정해주기
            counts[num] = 1

        i += 1  # 다음 인덱스로 이동

    # 사용된 숫자의 종류 개수 출력 (딕셔너리의 키 개수)
    print("{}에서 사용된 숫자의 종류는 {}개입니다.".format(member, len(counts)))

    # 각 숫자별 개수 출력(숫자 오름차순으로 보기 좋게)
    parts = []  # "숫자 : 개수" 문자열들을 담을 리스트
    for key in sorted(counts):  # 키를 오름차순으로 정렬
        parts.append("{} : {}개".format(key, counts[key]))  # 문자열을 만들어 추가
    print(" / ".join(parts))  # 리스트를 " / "로 이어 출력
    print("-"*60)

    print()
    print("2번 문제")
    print("-"*60)
    dna = input("염기 서열을 입력하세요: ").strip().upper()#.strip().upper -> 문자열 전처리 
    # strip() : 문자열 앞뒤에 공백 제거
    # upper() : 문자열을 대문자로 바꿔줌.
    # 현 단계까지에선 "숫자", "한글"은 제거 안함. 영어에만 세팅을 줌.
    
    
    # 각 염기의 개수를 저장할 딕셔너리
    base_counts = {"A": 0, "T": 0, "G": 0, "C": 0}

    # A, T, G, C 외의 문자는 제외한 문자열로 다시 만든다
    filtered = []#필터된 염기서열 저장하기
    i = 0
    while i < len(dna):
        ch = dna[i]
        if ch in base_counts:
            filtered.append(ch)#딕셔너리와 겹치는 것만 따로 뺴둠.
        i += 1
    dna = "".join(filtered)
    #print("dna = ", dna)

    # 필터와 동시에 갯수 누적보단 필터된 애들을 다시 확인 후에 누적확인함.
    i = 0
    while i < len(dna):
        base = dna[i]
        base_counts[base] += 1  # 여기서는 이미 A, T, G, C만 남아 있음
        i += 1

   
    print("A : {}개 / T : {}개 / G : {}개 / C : {}개".format(
        base_counts["A"], base_counts["T"], base_counts["G"], base_counts["C"]
    ))
    print("-"*60)
    
    print("3번 문제")
    print("-"*60)
    print("염기 코돈 갯수는 위에서 입력받은 염기서열을 쓴다.(2번문제 참고)")
    
    i=0
    count =0
    dna_codun = {} # 염기서열을 3개씩 나눈것들을 딕셔너리로 저장
    while i < len(dna):
        i += 1
        if i % 3 == 0:
            count+=1
            dna_codun[count] = dna[i-3:i]
    print("코돈은 총 {}개 입니다.".format(count))
    print("codun = ", dna_codun)
    
        
    print("-"*60)
    print("4번 문제")
    print("-"*60)
    
    
    taget_List = [1, 2, [3, 4, [5, 6]], 7, [8, 9]]
    print("평탄화 할 리스트 : ", taget_List)
    print()

    # 모든 중첩 리스트를 평탄화(깊이가 몇 단계이든 가능)
    flatten_List = []
    stack = [taget_List]  # 처리할 대상을 스택에 넣는다
    while len(stack) > 0:
        current = stack.pop()  # 마지막 요소 꺼내기
        if type(current) is list:
            # 리스트면 내부 요소를 역순으로 스택에 넣어 원래 순서를 유지한다
            i = len(current) - 1
            while i >= 0:
                stack.append(current[i])
                i -= 1
        else:
            # 리스트가 아니면 결과에 추가
            flatten_List.append(current)

    print("평탄화된 리스트 : ", flatten_List)
    print("-"*60)
    
    
    
    
    
    
    pass


if __name__ == "__main__":
    main()
