"""
    제작 시간 : 0309_15:36
    유형 : 연습
    주제 : 연습 문제 _ 간략 pdf p.207
    문제 설명 : for문 연습하기
    - 1. for문으로 4의 배수 아닌 수
    - 2. for문으로 길이 환산표 만들기
    - 3. 리스트로 만든 영어 스펠링 퀴즈
    - 4. 리스트 성적 합계/평균
    
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
    # input = sys.stdin.readline
    # out_lines: list[str] = []
    
    #        입 력
    count = 0
    for i in range(800, 900):
        if i % 4 != 0:
            print("%4d" % i, end=" ")
            count += 1
            if count % 10 == 0:
                print()
    print('\n')
   
    print('-' * 60)  # 표 상단 구분선 출력
    #print(f"{'cm':>4}\t{'mm':>8}\t{'m':>8}\t{'inch':>8}")  # 헤더: 단위 이름을 열 정렬에 맞춰 출력
    print("\tcm\tmm\tm\tinch")
    print('-' * 60)  # 헤더 아래 구분선 출력

    for cm in range(70, 90, 2):  # 70부터 88까지 2cm 간격으로 반복
        mm = cm * 10.0  # cm -> mm 변환 (1cm = 10mm)
        m = cm / 100.0  # cm -> m 변환 (100cm = 1m)
        inch = cm * 0.3937  # cm -> inch 변환 (1cm ≈ 0.3937 inch)
        #print(f"{cm:4d}\t{mm:8.1f}\t{m:8.2f}\t{inch:8.1f}")  # 각 단위 값 출력
        print("\t", cm , "\t", mm , "\t", m , "\t", inch)
    print('-' * 60)  # 표 하단 구분선 출력
    
    
    questions = ['tr_in', 'b_s', '_axi', 'suss_ss']
    answers=['a', 'u', 't', 'e']
    count = 0
    print("빈칸에 알맞은 단어를 입력하시오.")
    for i in range(len(questions)):
        question = questions[i]
        answer = answers[i]
        input_answer = input(f"{question} : ")
        if input_answer == answer:
            print("정답입니다.")
            count= count+1
        else:
            print("오답입니다.")
    print("총 {}개 맞추셨습니다.".format(count))
    print("-" * 60)
    
    score = []
    
    while True:
        x = int(input("성적 입력 : "))
        if x==-1:
            break
        else:
            score.append(x)
    print(score)
    sum=0
    for i in range(0,int(len(score))):
        sum += score[i]
    #for score in scores:
    #    sum += score
    if(len(score)!=0):
        avg = sum / len(score)
    else:
        avg = 0
    
    print("합계 : ", sum)
    print("평균 : ", avg)
    
    
    pass


if __name__ == "__main__":
    main()
    
