"""
    제작 시간 : 0311
    유형 : 과제 (개선 버전)
    주제 : 4지선다 문제 은행
    설명 :
    - 한국어 단어를 보고 영어 단어를 맞히는 문제를 랜덤으로 출제
    - 문제 수 입력 -> 중복 없이 선택 -> 보기 생성 -> 채점 -> 최종 점수 출력
"""

from __future__ import annotations

import random
from typing import List, Tuple

# 문제 은행: (한글, 영어) 튜플의 리스트
QUESTIONS: List[Tuple[str, str]] = [
    ("사과", "apple"),
    ("책", "book"),
    ("친구", "friend"),
    ("호랑이", "tiger"),
    ("가수", "singer"),
    ("사랑", "love"),
    ("요리사", "cook"),
    ("거북이", "turtle"),
    ("사자", "lion"),
    ("고양이", "cat"),
]

CHOICE_COUNT = 4  # 4지선다


def input_int(prompt: str, min_value: int, max_value: int) -> int:
    """지정 범위 내의 정수를 입력받아 반환한다."""
    while True:
        text = input(prompt).strip()
        if not text.isdigit():
            print("숫자로 입력해 주세요.")
            continue
        value = int(text)
        if not (min_value <= value <= max_value):
            print(f"{min_value} ~ {max_value} 사이의 숫자를 입력해 주세요.")
            continue
        return value


def build_answer_pool(questions: List[Tuple[str, str]]) -> List[str]:
    """정답(영어) 후보 리스트를 생성한다."""
    return [eng for _, eng in questions]


def make_choices(correct: str, pool: List[str], rng: random.Random) -> List[str]:
    """정답 1개 + 오답 3개로 보기 4개를 만든다."""
    wrong_pool = [w for w in pool if w != correct]
    if len(wrong_pool) < CHOICE_COUNT - 1:
        raise ValueError("보기 생성에 필요한 오답 후보가 부족합니다.")
    choices = rng.sample(wrong_pool, k=CHOICE_COUNT - 1) + [correct]
    rng.shuffle(choices)
    return choices


def ask_question(
    index: int,
    korean: str,
    correct: str,
    choices: List[str],
) -> bool:
    """문제를 출력하고 정답 여부를 반환한다."""
    print(f"{index}. '{korean}'의 뜻을 가진 영어 단어는 무엇인가요?")
    for i, option in enumerate(choices, start=1):
        print(f"  {i}. {option}")

    answer = input_int("정답 번호(1~4): ", 1, len(choices))
    if choices[answer - 1] == correct:
        print("정답입니다.")
        return True

    print(f"오답입니다. 정답은 {correct} 입니다.")
    return False


def main() -> None:
    rng = random.Random()

    # 문제 수 입력
    max_count = len(QUESTIONS)
    count = input_int(f"몇 문제를 푸시겠습니까? (1~{max_count}) : ", 1, max_count)

    # 문제 선택(중복 없이)
    selected = rng.sample(QUESTIONS, k=count)

    # 보기 생성을 위한 전체 정답 풀
    answer_pool = build_answer_pool(QUESTIONS)

    score = 0
    for i, (korean, correct) in enumerate(selected, start=1):
        choices = make_choices(correct, answer_pool, rng)
        if ask_question(i, korean, correct, choices):
            score += 1
        print()

    print(f"총 {count}문제 중 {score}문제 맞혔습니다.")


if __name__ == "__main__":
    main()
