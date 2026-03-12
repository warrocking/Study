"""
    제작 시간 : 0312_10:45
    유형 : 예제
    주제 : ㅔ252 
    문제 설명 : 
    - 문자열, 리스트, 딕셔너리와 관련되 기본 함수
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
    
    print("# reversed() 함수")
    list_a = [1, 2, 3, 4, 5]
    list_reversed = reversed(list_a)
    print("# reversed() 함수")
    print("reversed([1, 2, 3, 4, 5]) : ", list_a)
    print("list(reversed([1, 2, 3, 4, 5])) : ", list(list_reversed))
    print()
    
    print(" # enumerate() 함수")
    example_list = ["요소A", "요소B", "요소C"]
    print("# 단순 출력")
    print("example_list = ",example_list)
    print("# enumerate() 함수 적용 출력")
    print("변환 후 : ",enumerate(example_list))
    print()
    
    print("# list() 함수로 강제 변환")
    print("변환 : ", list(enumerate(example_list)))
    print()
    
    print("# 반복문과 조합하기")
    for i , value in enumerate(example_list):
        print("{}번째 요소는 {}입니다.".format(i, value))
    print()
    
    print("# 딕셔너리의 item() 함수와 반복문")
    example_dictionary = {
        "키A" : "값A",
        "키B" : "값B",
        "키C" : "값C"
    }
    print("# 딕셔너리의 items() 함수")
    print("items() : ", example_dictionary.items())
    print()
    
    print("# 딕셔너리의 items() 함수와 반복문 조합하기")
    for key, element in example_dictionary.items():
        print("dictionary[{}] = {}".format(key, element))
    print()
    
    print("# 반복문을 사용한 리스트 작성")
    array = []
    for i in range(0, 20, 2):
        array.append(i*i)
    print(array)
    print()
    
    print("# 조건을 활용한 리스트 내포")
    array = ["사과", "자두", "초콜릿", "바나나", "체리"]
    print(array)
    print("변환 리스트 : ", end = "")
    output = [fruit for fruit in array if fruit != "초콜릿"]
    # array의 요소를 fruit이라고 할 때 초콜릿이 아닌 fruit으로 리스트를 재조합해 주세요 
    print(output)
    print()
    
    
    print("# if 조건문과 여러 줄 문자열(1)")
    number = int(input("정수 입력 : "))
    
    if number % 2 ==0:
        print("""\
        입력한 문자열은 {}입니다.
        {}는 짝수입니다.""".format(number, number))
    else:
        print("""\
        입력한 문자열은 {}입니다.
        {}는 홀수입니다.""".format(number, number))
    print()
    
    print("# if 조건문과 여러 줄 문자열(2)")
    number = int(input("정수 입력 : "))
    
    if number % 2 == 0:
        print("""\
        입력한 문자열은 {}입니다.
        {}는 짝수입니다.""".format(number, number))
    else:
        print("""\
        입력한 문자열은 {}입니다.
        {}는 홀수입니다.""".format(number, number))
    print()
    
    print("# 괄호로 문자열 연결하기")
    test = (
        "이렇게 입력해도 "
        "하나의 문자열로 연결되어 "
        "생성됩니다."
    )  
    print("test : ", test)
    print("type(test) : ", type(test))
    print()
    
    # 튜플 자료형 구분
    # 위의 test가 튜플형이 아니다.
    # 괄호 내부의 문자열이 다음과 같이 쉼표로 연결되어야 튜플이다.
    
    print(" # 여러 줄 문자열과 if 구문을 조합했을 떄의 문제 해결")
    number = int(input("정수 입력 : "))
    if number % 2 == 0:
        print("\n".join(
            [
                "입력한 문자열은 {}입니다.".format(number),
                "{}는 짝수입니다.".format(number)
            ]
        ))
    else:
        print("\n".join(
            [
                "입력한 문자열은 {}입니다.".format(number),
                "{}는 홀수입니다.".format(number)
            ]
        ))
    print()
    
    
    print("# 이터레이터")
    numbers = [1, 2, 3, 4, 5, 6]
    r_num = reversed(numbers)
    
    # reversed_number를 출력
    print("reversed_numbers : ", r_num)
    print(next(r_num))
    print(next(r_num))
    print(next(r_num))
    print(next(r_num))
    print(next(r_num))
    print(next(r_num))
    print()
    
    '''
    1. reversed() 함수는 매개변수에 리스트를 넣으면 요소의 순서를 뒤집을 수 있다.
    2. enumerate() 함수는 매개변수에 리스트를 넣으면 인덱스와 값을 쌍으로 사용해 반복문을 돌릴 수 있다.
    3. items() 함수는 키와 쌍으로 사용해 반복문을 돌릴 수 있게 해주는 딕셔너리 함수이다.
    4. 리스트 내포는 반복문과 조건문을 대괄호 [] 안에 넣는 형태를 사용해서 리스트를 생성하는 파이썬의 특수한 구문이다.
        'list comprehensions'도 기억해라.
    
    
    '''
    
    
    
    
    
    pass


if __name__ == "__main__":
    
    main()