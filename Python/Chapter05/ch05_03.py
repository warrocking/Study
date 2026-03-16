"""
    제작 시간 : 0313_10:47
    유형 : 예제
    주제 : 함수 고급
    문제 설명 : 
    - 키워드 : 튜플 / 콜백 함수 / 람다 / with 구문
"""

# 기본 모듈
import sys

# 함수 선언/정의 (필요 시 작성)



def main() -> None:
    # 변수 선언 및 초기화
    # 튜플 테스트
    tuple_test_1 = (10, 20, 30)
    print("tuple_test[0] : ", tuple_test_1[0])
    print("tuple_test[1] : ", tuple_test_1[1])
    print("tuple_test[2] : ", tuple_test_1[2])
    
    try:
        tuple_test_1[0] =1
        # 튜플은 생성 후 값 변경이 안된다. 값을 변경하려고 하면 오류가 출력된다.
    except:
        pass
    print()
    
    # 리스트와 튜플의 특이한 사용
    [a, b] = [10, 20]#리스트
    (c, d) = (10, 20)#튜플
    print("a : ", a)
    print("b : ", b)
    print("c : ", c)
    print("d : ", d)
    
    print()
    
    # 괄호가 없는 튜플
    tuple_test_2 = 10, 20, 30, 40
    print("괄호가 없는 튜플의 값과 자료형 출력")
    print("tuple_test_2 : ", tuple_test_2)
    print("type(tuple_test_2) : ", type(tuple_test_2))
    # 괄호가 없는 튜플 활용
    a, b, c = 10, 20, 30
    print("#괄호가 없는 튜플을 활용한 할당")
    print("a : ", a)
    print("b : ", b)
    print("c : ", c)
    print()
    
    # 변수의 값을 교환하는 튜플
    a, b = 10, 20
    print("# 값을 교환하기 전")
    print("a : ", a)
    print("b : ", b)
    a, b = b, a
    print("# 값을 교환한 후")
    print("a : ", a)
    print("b : ", b)
    print()
    
    # 튜플과 함수
    def test():
        return (10, 20)
    a, b = test()
    print("a : ", a)
    print("b : ", b)
    print()
    
    # 람다 : 함수라는 '기능'을 매개변수로 전달하는 코드
    # 함수의 매개변수로 함수 전달하기
    def call_10_times(func):
        for i in range(10):
            func()
    def print_hello():
        print("안녕하세요")
    call_10_times(print_hello)

    # map() : 리스트의 요소를 함수에 넣고 리턴된 값으로 새로운 리스트를 구성하는 함수
    # map(함수 , 리스트)
    # filter() : 리스트의 요소를 함수에 넣고 리턴된 값이 True인 것으로, 새로운 리스트를 구성하는 함수
    # filter(함수 , 리스트)
    def power(item):
        return item * item
    def power2(item):
        return item **2
    def under_3(item):
        return item < 3
    list_a = [1, 2, 3, 4, 5]
    output_a = map(power, list_a)
    print("map() 함수의 실행 결과")
    print("map(power, list_a) : ", output_a)
    print("map(power, list_a) : ", list(output_a))
    # output_a = map(power2, list_a)
    # print("map() 함수의 실행 결과")
    # print("map(power2, list_a) : ", output_a)
    # print("power2 = ", list(output_a))

    data = [1, 2, None, 3, 4, 5, None, 6, 7, 8, 9, None]
    def filter_None(item):
        # if item == None:
        #     return False
        # else:
        #     return True
        return not item # None 자체가 False 이기 때문에 # '0' 도 걸러짐
    output_a = filter(filter_None, data)
    print("filter() 함수의 실행 결과")
    print("filter(filter_None, data) : ", output_a)
    print("filter(filter_None, data) : ", list(output_a))
    
    
    print()
    
    
    print()
    print()
    output_b = filter(under_3, list_a)
    print("filter() 함수의 실행 결과")
    print("filter(under_3, list_a) : ", output_b)
    print("filter(under_3, list_a) : ", list(output_b))
    # 람다의 개념
    # 간단한 함수를 쉽게 선언하는 방법
    power = lambda x: x*x
    under_3 = lambda x: x<3
    list_input_a = [1,2,3,4,5]
    
    output_a = map(power, list_input_a)
    print("map() 함수의 실행 결과")
    print("map(power, list_input_a) : ", output_a)
    print("map(power, list_input_a) : ", list(output_a))
    print()

    output_b = filter(under_3, list_input_a)
    print("filter() 함수의 실행 결과")
    print("filter(under_3, list_input_a) : ", output_b)
    print("filter(under_3, list_input_a) : ", list(output_b))
    print()
    
    output_a = map(lambda x: x*x, list_input_a)
    print("map() 함수의 실행 결과")
    print("map(lambda x: x*x, list_input_a) : ", output_a)
    print("map(lambda x: x*x, list_input_a) : ", list(output_a))
    print()
    output_b = filter(lambda x: x<3, list_input_a)
    print("filter() 함수의 실행 결과")
    print("filter(lambda x: x<3, list_input_a) : ", output_b)
    print("filter(lambda x: x<3, list_input_a) : ", list(output_b))
    print()
    
    
    
    #---------------------
    # 프로그램 open
    file = open("basic.txt", "w", encoding="utf-8")
    file.write("Hello Python")
    file.close()
    
    # with 키워드
    # 조건문과 반복문이 들어가다 보면 파일을 열고 닫지 않는 실수를 하는 경우가 생길 수 있음.
    # 이런 실수 방지를 위해 with키워드가 있다.
    
    with open("basic.txt", "w", encoding="utf-8") as file:
        file.write("Hello Pythonss")
    #위와 같이 작성하면 with 구문이 종료될 때 자동으로 파일이 닫힘.
    
    with open("basic.txt", "r") as file:
        contents = file.read()
    print(contents)
    
    # 랜덤하게 1000명의 키와 몸무게 만들기
    import random
    hanguls =list("가나다라마바사아자차카타파하")
    with open("info.txt", "w") as file:
        for i in range(1000):
            name = random.choice(hanguls) + random.choice(hanguls)
            weight = random.randrange(40, 100)
            height = random.randrange(140, 200)
            file.write("{}, {}, {}\n".format(name, weight, height))
    
    with open("info.txt", "r") as file:
        for line in file:
            (name, weight, height) = line.strip().split(", ")
            if(not name or not weight or not height):
                continue
            bmi = int(weight)/((int(height)/100)**2)
            result = ""
            if(25<=bmi):
                result = "과체중"
            elif(18.5<=bmi):
                result = "정상체중"
            else:
                result = "저체중"
            
            print("\n".join([
                "이름 : {}",
                "몸무게 : {}",
                "키 : {}",
                "BMI : {}",
                "결과 : {}"
            ]).format(name, weight, height, bmi, result))
            print()
    
    # 제너레이터
    # 파이썬의 특수한 문법 구조.
    # 이터레이터를 직접 만들 때 사용하는 코드.
    # 함수 내부에 yield 키워드를 사용하면 해당 함수는 제너레이터 함수가 되며, 일반함수와는 달리 함수를 호출해도 함수 내부의 코드가 실행되지 않음.
    
    def test():
        print("함수가 호출되었습니다.")
        yield "test"
    
    print("A 지점 통과")
    test()
    
    print("B 지점 통과")
    test()
    print(test())
    
    # 제네레이터 객체와 next() 함수
    def test():
        print("A 지점 통과")
        yield 1
        print("B 지점 통과")
        yield 2
        print("C 지점 통과")

    output = test()
    print("D 지점 통과")
    a = next(output)
    print(a)
    print("E 지점 통과")
    b = next(output)
    print(b)
    print("F 지점 통과")
    c = next(output)
    print(c)
    next(output)
    
    
    
    
if __name__ == "__main__":
    main()