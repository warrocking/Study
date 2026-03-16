"""
    제작 시간 : 0313_12:15
    유형 : 과제
    주제 : 화면 출력 등의 이번 프로젝트의 GameManager 코드
    문제 설명 : 
    - 화면에 뭐가, 무엇을, 어떻게 출력할 것인지 정하는 코드
    
    - 코드 과정
    - hip data 선언 및 초기화 
    - while문으로 끝날때 까지 무한 반복
        - "몇번 뽑을것인가" 등의 뽑기 횟수 질문
        - 최소 5회, 최대 20회의 조건에 만족하면 다음과정
        - 만족하지 않으면 다시 질문
        - 횟수, 만원 등이 어떻게 질문 받더라도 넘길 수 있게 오차 범위까지 받는 널널한 조건문으로 하기
    - 횟수에 맞게 로또 6개 출력해주기
        - ex) 6번 하기 ->   {1, 2, 3, 4, 5, 6} / {7, 8, 9, 10, 11, 12} / {13, 14, 15, 16, 17, 18} /
                            {19, 20, 21, 22, 23, 24} / {25, 26, 27, 28, 29, 30} / { 31, 32, 33, 34, 35, 36}
        - 위와 같이 횟수에 맞게 번호 출력
        - 단, 위에선 번호 겹침이 없지만, 로또 번호 6개 내에서만 중복이 없고, 각 횟수에 대해서는 서로 간섭이 없음. 즉 겹쳐도 됨.
"""

# 기본 모듈
import sys
import random
from Random import Random
#from tkinter import *
from Project_Lotto.Code.Data_AI import load_Json, make_Json, save_Json, check_Json

def control_panel(num):
    if(num==1):
        Control_Panel.buy_Lotto()
    elif(num==2):
        Control_Panel.check_Lotto()
    elif(num==3):
        Control_Panel.check_Probability()
    elif(num==4):
        Control_Panel.check_Data()
    elif(num==5):
        sys.exit()
# control 패널 안의 종류
class Control_Panel:
    def check_input_int(prompt="", min_value=None, max_value=None):
        while True:
            s = input(prompt).strip()
            try:
                value = int(s)
            except ValueError:
                print("입력을 잘못했습니다. 다시 입력해주세요.")
                continue
            if min_value is not None and value < min_value:
                print(f"{min_value} 이상으로 입력해주세요.")
                continue
            if max_value is not None and value > max_value:
                print(f"{max_value} 이하로 입력해주세요.")
                continue
            return value

    def buy_Lotto():
        Record_Lotto = {}
        count = Control_Panel.check_input_int("몇 장이 필요하신가요? (5~20): ", 5, 20)
        print(f"{count}장을 구매했습니다.")
        while(True):
            price = count * 5000
            #input_price = int(input("{}원 주세요. : ".format(price)))
            input_price = Control_Panel.check_input_int("{}원 주세요. : ".format(price))
            if(input_price>=price):
                change = input_price - price
                print("거스름돈 : {} , {}장 뽑아서 드리겠습니다.".format(change, count))
                break
            else:
                print("돈이 부족해요. 돈을 줄테니 다시 돈을 주세요.")
                
        for i in range(0,count*5):
            if(i%5==0):
                print("\n{}번째 장".format(i//5+1))
            list_print = Random(6, 1, 46)
            bonus_num = Random(1, 1, 46, False, list_print)
            list_print.append(bonus_num)
            print("{}회 : {} + 보너스 : {}".format(i%5 +1, list_print[0:5], list_print[-1]))
            Record_Lotto[i] = list_print
        save_Json(Record_Lotto)
    def check_Lotto():
        
        
        pass
    
    def check_Probability():
        pass
    
    def check_Data():
        pass
   
    
    

def main() -> None:

    print("복권 판매점")
    while(True):
        print()
        print("1. 로또 구매")
        print("2. 로또 결과 확인")
        print("3. 로또 확률 확인")
        print("4. 데이터 확인")
        print("5. 시스템 종료")

        control = int(input(" : "))
        if(type(control)==int):
            if(1<=control<=5):
                control_panel(control)
            else:
                print("숫자만 입력해주세요")
        
    
    
    
        
        
    
    
    pass


if __name__ == "__main__":
    main()
