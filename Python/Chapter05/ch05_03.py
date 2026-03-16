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

if __name__ == "__main__":
    main()