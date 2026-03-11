"""
    제작 시간 : 0311_12:18
    유형 : 과제
    주제 : 4가지 목록 중 하나를 선택해서, 답을 맞힌다.
    문제 설명 : 
    - 문제 종류는 아래와 같다.
        - 사과 : apple
        - 책 : book
        - 친구 : friend
        - 호랑이 : tiger
        - 가수 : singer
    - ex
        - '책'의 영어 단어는?
            - 1. friend
            - 2. tiger
            - 3. singer
            - 4. book
            - 정답 : 4
    
    - 흐름도
        - 1. 시작
        - 2. 문제 은행 딕셔너리 생성
        - 3. 딕셔너리 키의 리스트 생성 & 딕셔너리의 인덱스 리스트 생성
        - 4. 인덱스 리스트에서 하나의 요소 랜덤 추출
        - 5. 문제 제목과 사지선다 보기 출력
        - 6-1. 사지선다 문제가 다 처리 되었다면 종료
        - 6-2. 사지선다 문제가 다 처리되지 않았다면 4로 이동
"""

# 기본 모듈
import sys  # 시스템 관련 모듈(현재 코드는 사용하지 않지만 유지)
import random  # 랜덤 선택을 위해 사용
# 추가 모듈 (필요 시 주석 해제)
# import math
# import itertools
# import collections

# 함수 선언/정의 (필요 시 작성)
# def helper():
#     pass
# Question 딕셔너리 구조:
# - 바깥 키: 문제 번호(문자열)
# - 바깥 값: {한글: 영어} 형태의 내부 딕셔너리
Question = {
    '1' : {'사과' : 'apple'},
    '2' : {'책' : 'book'},
    '3' : {'친구' : 'friend'},
    '4' : {'호랑이' : 'tiger'},
    '5' : {'가수' : 'singer'},
    '6' : {'사랑' : 'love'},
    '7' : {'요리사' : 'cook'},
    '8' : {'거북이' : 'turtle'},
    '9' : {'사자' : 'lion'},
    '10' : {'고양이' : 'cat'},
}

def main() -> None:
    # 문제 수 입력 및 검증
    # 사용자가 적절한 개수를 입력할 때까지 반복
    while True:
        # input()으로 문자열을 받고 strip()으로 공백 제거
        index_str = input("몇 문제를 푸시겠습니까? : ").strip()
        # int로 변환하여 비교(숫자가 아니면 오류가 날 수 있음)
        if(not index_str.isdigit()):
            print("숫자만 입력해주세요.\n")
        elif (len(Question) <= int(index_str)):
            print("문제 최대치를 넘었습니다. 다시 입력해주세요.\n")
        elif (int(index_str) <= 0):
            print("너무 작을 수를 입력하였습니다. 다시 입력해주세요.\n")
        else:
            print("총 {}문제 선택하였습니다.\n".format(index_str))
            break
    
    # 문자열을 정수로 변환
    index = int(index_str)
    
    # 문제 번호를 중복 없이 뽑는다
    # list(Question.keys()) -> 문제 번호들의 리스트
    # random.sample(..., k=index) -> 중복 없이 k개 뽑기
    question_ids = random.sample(list(Question.keys()), k=index)
    print("question_ids : ", question_ids)  # 확인용 출력(디버그)
    # 전체 영어 정답 목록(보기 만들 때 사용)
    # Question.values()는 내부 딕셔너리들의 리스트
    # list(q.values())[0] -> 내부 딕셔너리의 영어 단어 하나 꺼내기
    all_answers = [list(q.values())[0] for q in Question.values()]
    print("{} : {}".format(question_ids, all_answers))  # 확인용 출력(디버그)
    
    score = 0  # 맞힌 개수
    # enumerate(..., start=1): 문제 번호를 1부터 시작해서 함께 받기
    for i, qid in enumerate(question_ids, start=1):
        qa = Question[qid]  # 선택된 문제의 내부 딕셔너리
        korean_word = next(iter(qa.keys()))  # 한글 단어(키) 꺼내기
        correct = qa[korean_word]  # 정답 영어 단어(값) 꺼내기

        # 보기 4개 만들기(정답 1 + 오답 3)
        # wrong_answers: 정답을 제외한 오답 후보들
        wrong_answers = [a for a in all_answers if a != correct]
        # 오답 3개를 랜덤 선택한 뒤 정답을 섞어 4지선다 구성
        choices = random.sample(wrong_answers, k=3) + [correct]
        random.shuffle(choices)  # 보기 순서 섞기

        # 문제 출력
        print("{}. '{}'의 뜻을 가진 영어 단어는 무엇인가요?".format(i, korean_word))
        for idx, opt in enumerate(choices, start=1):
            print(f"  {idx}. {opt}")

        # 답 입력 및 판정
        ans = input("정답 번호: ").strip()  # 문자열로 입력 받기
        # 숫자이고 1~4 범위인지 확인
        if ans.isdigit() and 1 <= int(ans) <= 4:
            # 번호에 해당하는 보기가 정답이면 점수 증가
            if choices[int(ans) - 1] == correct:
                print("정답입니다.")
                score += 1
            else:
                print(f"오답입니다. 정답은 {correct} 입니다.")
        else:
            print("잘못된 입력입니다. 정답 처리하지 않습니다.")
        print()

    # 최종 점수 출력
    print(f"총 {index}문제 중 {score}문제 맞혔습니다.")


if __name__ == "__main__":
    main()
