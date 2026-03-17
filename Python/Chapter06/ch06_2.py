"""
    제작 시간 : 0317_11:18
    유형 : 예제
    주제 : 예외 고급
    문제 설명 : 
    - 핵심 키워드 : 예외 객체 , raise 구문 , 깃허브
"""

# 기본 모듈
import sys

 # 예외 객체
def except01():
    try:
        number_input_a = int(input("정수입력 > "))
        print("원의 반지름 : ", 2 * 3.14 * number_input_a)
        print("원의 넓이 : ", 3.14*(number_input_a**2))
    except Exception as exception:
        print("type(exception) : ", type(exception))
        print("exception : ", exception)

def except02():
    list_number = [52, 273, 32, 72, 100]
    try:
        number_input = int(input("정수 입력 > "))
        print("{}번째 요소 : {}".format(number_input, list_number[number_input]))
    except Exception as exception:
        print("type(exception) : ", type(exception))
        print("exception : ", exception)


def except_multi():
    list_number = [52, 273, 32, 72, 100]
    
    try:
        number_input = int(input("정수 입력 > "))
        print("{}번째 요소 : {}".format(number_input, list_number[number_input]))
    except ValueError:
        # ValueError 가 발생한 경우
        print("정수를 입력해주세요.")
    except IndexError:
        print("리스트의 인덱스를 벗어났다")

def except_as():
    list_number = [52, 273, 32, 72, 100]
    
    try:
        number_input = int(input("정수 입력 > "))
        print("{}번쨰 요소 : {}".format(number_input, list_number[number_input]))
    except ValueError as exception:
        print("정수를 입력해 주세요.")
        print("exception : ", exception)
    except IndexError as exception:
        print("리스트의 인덱스를 벗어났다.")
        print("exception : ", exception)

def except03():
    list_number = [52,273, 32, 72, 100]
    try:
        numberInput = int(input("정수 입력 : "))
        print("{}번째 요소 : {}".format(numberInput, list_number[numberInput]))
        예외발생시키기()
    except ValueError as exception:
        print("정수를 입력해주세요")
        print(type(exception), exception)
    except IndexError as exception:
        print("리스트의 인덱스를 벗어남")
        print(type(exception), exception)

def except_all():
    list_number = [52, 273, 32, 72, 100]
    
    try:
        numberInput = int(input("정수 입력 > "))
        print("{}번째 요소 : {}".format(numberInput, list_number[numberInput]))
        예외발생()
    except ValueError as exception:
        print("정수를 입력해주세요")
        print(type(exception), exception)
    except IndexError as exception:
        print("리스트의 인덱스를 벗어남")
        print(type(exception), exception)
    except Exception as exception:
        print("미리 파악하지 못한 예외가 발생함")
        print(type(exception), exception)

def _raise():
    number = input("정수 입력 > ")
    number = int(number)
    
    if number>0:
        raise NotImplementedError
    else:
        raise NotImplementedError
    pass


#-------------------------------------------------------
#-------------------------------------------------------
def main() -> None:

    _raise()


if __name__ == "__main__":
    main()