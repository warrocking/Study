"""
    제작 시간 : 0309_17:50
    유형 : 연습
    주제 : p.227~229 연습문제
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
    # 변수 선언 및 초기화
    print("p.227 1번 문제")
    """
        dict_a의 값         dic_a에 적용할 코드         dict_a의 결과
        ------------------------------------------------------------
            {}                                        {'name' : '구름'}
        {"name" : "구름"}                                   {}
    """
    dict_a = {}
    dict_a["name"]= "구름"
    print(dict_a)
    print()
    print("-"*60)
    print()
    del dict_a["name"]
    print(dict_a)
    print()
    print("-"*60)
    print()
    print("p.227 2번 문제")
    pets = [
        {"name" : "구름", "age" : 5},
        {"name" : "초코", "age" : 3},
        {"name" : "아지", "age" : 1},
        {"name" : "호랑이", "age" : 1}
    ]
    print(" # 우리 동네 애완 동물들")
    for i in range(0, len(pets)):
        print(pets[i]["name"], str(pets[i]["age"]) + "살")
    print()
    print("-"*60)
    print()
    print("p.228 3번 문제")
    numbers = [1, 2, 6, 8, 4, 3, 2, 1, 9, 5, 4, 9, 7, 2, 1, 3, 5, 4, 8, 9, 7, 2, 3]
    counter = {}
    for number in numbers:
        if number in counter:
            counter[number] = counter[number] + 1
        else:
            counter[number] = 1
    print(counter)
    print()
    print("-"*60)
    print()
    print("p.229 4번 문제")
    # type("문자열") is str # 문자열인지 확인
    # type([]) is list      # 리스트인지 확인
    # type({}) is dict      # 딕셔너리인지 확인
    
    character = {
        "name" : "기사",
        "level" : 12,
        "items" : {
            "sword" : "불꽃의 검",
            "armor" : "풀플레이트"
        },
        "skill" : ["베기", "세게 베기", "아주 세게 베기"]
    }
    
    """
        name : 기사
        level : 12
        sword : 불꽃의 검
        armor : 풀플레이트
        skill : 베기
        skill : 세게 베기
        skill : 아주 세게 베기
    """
    
    """
    # character 딕셔너리를 한 개의 key씩 꺼내며 확인한다.
    # key는 "name", "level", "items", "skill" 순서로 들어온다(삽입 순서).
    for key in character:
        value = character[key]  # 현재 key에 해당하는 값을 가져온다

        # isinstance(값, 타입) -> 값이 해당 타입이면 True, 아니면 False를 반환하는 함수
        # 값이 딕셔너리라면: 내부 항목(sword, armor)을 펼쳐서 출력해야 한다.
        if isinstance(value, dict):
            # value.items()는 (키, 값) 쌍을 하나씩 꺼내준다.
            for sub_key, sub_value in value.items():
                print(f"{sub_key} : {sub_value}")  # 예: sword : 불꽃의 검

        # 값이 리스트라면: 리스트 항목을 하나씩 꺼내 같은 key로 여러 줄 출력한다.
        elif isinstance(value, list):
            for item in value:
                print(f"{key} : {item}")  # 예: skill : 베기

        # 값이 문자열/숫자 같은 기본 타입이면 그대로 한 줄 출력한다.
        else:
            print(f"{key} : {value}")  # 예: name : 기사, level : 12
    """
    # character 딕셔너리를 하나씩 순회한다.
    # key에는 "name", "level", "items", "skill" 같은 키가 들어온다.
    for key in character:
        value = character[key]  # 현재 key에 해당하는 실제 값을 꺼낸다.

        # type(값) is dict -> 값이 딕셔너리일 때만 True
        if type(value) is dict:
            # 딕셔너리라면 내부 항목을 펼쳐서 각각 출력한다.
            # 예: {"sword": "...", "armor": "..."} -> sword : ..., armor : ...
            for sub_key, sub_value in value.items():
                print(f"{sub_key} : {sub_value}")
        
        # type(값) is list -> 값이 리스트일 때만 True
        elif type(value) is list:
            # 리스트라면 항목을 하나씩 꺼내 같은 key 이름으로 여러 줄 출력한다.
            # 예: skill 리스트 -> skill : 베기 / skill : 세게 베기 ...
            for item in value:
                print(f"{key} : {item}")

        # 위 두 경우가 아니면 문자열/숫자 같은 기본 값으로 보고 그대로 출력한다.
        else:
            print(f"{key} : {value}")

    
    print()
    print("-"*60)
    print()
    
    #        입 력
    
    #        처 리
    
    #        출 력
    
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()
