"""
    제작 시간 : 0311_09:33
    유형 : 과제
    주제 : 바코드 암호화/복호화
    문제 설명 : 
    - 1. 시작
    - 2. 숫자입력
    - 3. 입력된 숫자와 자리수가 5~10
    - 3-1. No -> 2번으로 이동
    - 3-2. Yes -> 4번으로 이동
    - 4. 숫자를 바코드로 암호화
    - 5. 암호화된 바코드 출력
    - 6. 종료
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

# 암호화 함수
def barEncrypt(n):
    if n == '0':
        code = '||:::'
    elif n == '1':
        code = ':::||'
    elif n == '2':
        code = '::|:|'
    elif n == '3':
        code = '::||:'
    elif n == '4':
        code = ':|::|'
    elif n == '5':
        code = ':|:|:'  
    elif n == '6':
        code = ':||::'
    elif n == '7':
        code = '|:::|'
    elif n == '8':
        code = '|::|:'
    elif n == '9':
        code = '|:|::'
    else:
        code = "오류!"
    return code

# 복호화 함수
def decryption(n):
    if n == '||:::':
        code = '0'
    elif n == ':::||':
        code = '1'
    elif n == '::|:|':
        code = '2'
    elif n == '::||:':
        code = '3'
    elif n == ':|::|':
        code = '4'
    elif n == ':|:|:':  
        code = '5'
    elif n == ':||::':
        code = '6'
    elif n == '|:::|':
        code = '7'
    elif n == '|::|:':
        code = '8'
    elif n == '|:|::':
        code = '9'
    else:
        code = "오류!"
    return code


def main() -> None:
    # 변수 선언 및 초기화
    
    #        입 력
    
    # 숫자 입력 -> 암호화 과정
    barcode_string = input("5~10 자리 숫자를 입력하세요. : ")
    if(len(barcode_string) < 5 or len(barcode_string) > 10):
        while True:
            print("5자리 미만 혹은 10자리를 초과했습니다. 다시 입력해주세요.")
            print()
            barcode_string = input("5~10 자리 숫자를 입력하세요. : ")
            if 5<=len(barcode_string)<=10:
                break
        
    print()
    barcode_encryption = ""
    for i in range(0, len(barcode_string)):
        barcode_encryption = barcode_encryption + barEncrypt(barcode_string[i])
        
    print("생성된 바코드 : ", barcode_encryption)
    print("-"*60)
    print("복호화 과정")
    print()
    barcode_decryption = ""
    for i in range(0, len(barcode_encryption), 5):
        barcode_decryption = barcode_decryption + decryption(barcode_encryption[i:i+5])

    print("복호화된 숫자 : ", barcode_decryption)
   
    
    #        처 리
    
    #        출 력
    
    # sys.stdout.write(\"\n\".join(out_lines))
    pass


if __name__ == "__main__":
    main()