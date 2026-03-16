"""
    제작 시간 : 0316_16:29
    유형 : 예제
    주제 : 06-01 : 구문 오류와 예외
    문제 설명 : 핵심 키워드 : 구문 오류 , 예외(런타임 에러), 기본 예외 처리, try except 구문
    - 오류의 종류 : 프로그램 실행 전 발생한 오류 -> 구문오류, 프로그램 실행 후 발생한 오류->예외 or 런타임 오류
        - 구문 오류 : 



"""

# 기본 모듈
import sys
def handle_with_try():
    user_input_a = input("정수 입력 : ")
    
    if user_input_a.isdigit():
        number_input_a = int(user_input_a)
        print("원의 반지름 : ", number_input_a)
        print("원의 둘레 : ", 2*3.14*number_input_a)
        print("원의 넓이 : ", 3.14 * (number_input_a **2))
        
    else:
        print("정수를 입력하지 않았습니다.")        
    
    
    try:
        number_input_a = int(user_input_a)
        print("원의 반지름 : ", number_input_a)
        print("원의 둘레 : ", 2*3.14*number_input_a)
        print("원의 넓이 : ", 3.14 * (number_input_a **2))
    except:
        print("정수를 입력하지 않았습니다.")        
        
def try_pass():
    list_input_a = ["52", "273", "32", "스파이", "103"]
    
    list_number = []
    
    for item in list_input_a:
        try:
            float(item) # 예외가 발생하면 알아서 다음으로 진행은 안되겠지?
            list_number.append(item) # 예외 없이 통과했으면 list_number 리스트에 넣어줘
        except:
            pass
    
    print("{} 내부에 있는 숫자는 ".format(list_input_a))
    print("{}입니다.".format(list_number))

def try_except_else():
    try:
        number_input_a = float(input("정수 입력 : "))
    except:
        print("정수를 입력하지 않았습니다.")
    else:
        print("원의 반지름 : ", number_input_a)
        print("원의 둘레 : ", 2*3.14*number_input_a)
        print("원의 둘레 : ", 3.14*(number_input_a**2))
  
"""
    try:
        예외가 발생할 가능성이 있는 코드
    except:
        예외가 발생했을 때 실행할 코드
    else:
        예외가 발생하지 않았을 때 실행할 코드
    finally:
        무조건 실행할 코드    
        
    구문 조합 
    - try + except
    - try + except + else
    - try + except + finally
    - try + except + else + finally
    - try + finally
"""
def try_except_else_finally():
    try:
        number_input_a = int(input("정수 입력 : "))
        print("원의 반지름 : ", number_input_a)
        print("원의 둘레 : ", 2*3.14*number_input_a)
        print("원의 둘레 : ", 3.14*(number_input_a**2))
    except:
        print("정수를 입력하지 않았습니다.")
    else:
        print("예외가 발생하지 않았습니다.")
    finally:
        print("일단 프로그램이 어떻게든 끝났습니다.")
  
def file_closed01():
    try:
        file = open("info.txt", "w")
        file.close()
    except:
        print("오류가 발생했습니다.")
        
    print("# 파일이 재대로 닫혔는지 확인하기")
    print("file.closed", file.closed)  
  
  
def file_closed02():
    try:
        file = open("info.txt", "w")
        예외.발생해라()
        file.close()
    except:
        print("오류가 발생했습니다.")
        
    print("# 파일이 재대로 닫혔는지 확인하기")
    print('file closed : ', file.closed)
  

def file_closed3():
    try:
        file = open("info.txt", 'w')
        예외.발생
    except:
        print("오류가 발생했습니다.")
    finally:
        file.close()
    print("# 파일이 제대로 닫혔는지 확인하기")
    print("file closed : ", file.closed)
  
def file_closed04():
    try:
        file = open("info.txt", 'w')
        예외.발생
    except:
        print("오류가 발생했습니다.")
    file.close()
    print("# 파일이 제대로 닫혔는지 확인하기")
    print("file closed : ", file.closed)    
        
def try_return01():
    print("test() 함수의 첫 줄")
    try:
        print("try 구문 실행")
        return
        print("try 구문 뒤의 return")
    except:
        print("except 구문 실행")
    else:
        print("else 구문 실행")
    finally: #얘는 무조건 실행됨
        print("finally 구문 실행")
    print("test() 함수의 마지막 줄")

def try_return02():
    def write_text_file(filename, text):
        try:
            file = open(filename, 'w')
            return
            file.write(text)
        except:
            print("오류가 발생")
        finally:
            file.close()
    
    write_text_file("test.txt", "안녕하슈")
    
def finally_loop():
    print("프로그램 시작")
    while True:
        try:
            print("Try 구문 실행")
            break
            print("try 구문 break 뒤의 프린트문")
        except:
            print("except 구문 실행")
        finally:
            print("finally 구문 실행")
        print("while문 마지막 줄")
    print("프로그램 종료")

    
def main() -> None:
    
    finally_loop()
    
    
    
    pass


if __name__ == "__main__":
    main()