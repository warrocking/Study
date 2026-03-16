# 제너레이터
    # 파이썬의 특수한 문법 구조.
    # 이터레이터를 직접 만들 때 사용하는 코드.
    # 함수 내부에 yield 키워드를 사용하면 해당 함수는 제너레이터 함수가 되며, 일반함수와는 달리 함수를 호출해도 함수 내부의 코드가 실행되지 않음.
def main():
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
    # c = next(output)
    # print(c)
    #next(output)
    
    def count_up_to(n):
        i = 1
        while i< n:
            yield i
            i+=1
    g = count_up_to(3)
    print(next(g))
    print(next(g))
    nums = [10, 20, 30]      # iterable
    it = iter(nums)          # iterator로 변환
    print(next(it))          # 10
    #print(next(g))
    
    
if __name__ == "__main__":
    main()