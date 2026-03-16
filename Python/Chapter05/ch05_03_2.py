# map() : 리스트의 요소를 함수에 넣고 리턴된 값으로 새로운 리스트를 구성하는 함수
    # map(함수 , 리스트)
    # filter() : 리스트의 요소를 함수에 넣고 리턴된 값이 True인 것으로, 새로운 리스트를 구성하는 함수
    # filter(함수 , 리스트)
def main():
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
    
    list_number = [1, 2, 3, 4, 5]
    output_1 = filter(lambda x:x**2, list_number)
    print("output_1 : ", list[output_1])
    
    
    numbers = [1, 2, 3, 4, 5, 6]
    #print("::".join(map(str, numbers)))
    numbers = map(lambda s:str(s) , numbers)
    print("::".join(numbers))
    numbers = [1, 2, 3, 4, 5, 6]
    #print(*numbers, seq="::")
    names = ["김영준", "조명철"]
    print("::".join(names))
    
    numbers_ = list(range(1, 15 +1))
    
    print(" # 홀수만 추출하기")
    print(list(filter(lambda x:x%2==1, numbers_)))
    print()
    print(" # 3 이상 , 7 미만 추출하기")
    print(list(filter(lambda x: 3<=x<7, numbers_)))
    print()
    print(" # 제곱해서 50미만 추출하기")
    print(list(filter(lambda x: x<10, numbers_)))
    
    
    
    
    
    
    
    
    
    
    
    
    
if __name__ == "__main__":
    main()