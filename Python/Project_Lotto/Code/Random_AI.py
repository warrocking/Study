"""
    제작 시간 : 0313_16:29
    유형 : 과제
    주제 : 랜덤 시스템 라이브러리 구현
    문제 설명 : 
    - 라이브러리 코드를 구현하기
    - 어떤 곳에서도 사용가능하도록 구현을 목표함.
    - 뽑기 갯수는 기본 매개변수
    - 숫자범위 / 겹치기 가능 or 불가능 / 몇번 반복 후 값 출력할건지 
    / 기본1개에서 몇개까지 동시에 출력할건지 / 뽑기 후에 결과를 다음 뽑기에 넣을 건지 말건지 / 몇번 반복할건지
    등등을 가변 변수로 설정
    
    
"""
# 모듈
import random


def draw(
    count=6,
    range_min=1,
    range_max=45,
    overlap=False,
    include=None,
    exclude=None,
    sort_result=True,
    seed=None,
    bonus_count=0,
    bonus_from_remaining=True,
    repeat=1,
    return_stats=False,
):
    """
    범용 랜덤 뽑기 함수.

    Parameters
    count : 메인 뽑기 개수
    range_min, range_max : 번호 범위(양끝 포함)
    overlap : 중복 허용 여부 (True면 복원추출)
    include : 반드시 포함할 번호 목록
    exclude : 제외할 번호 목록
    sort_result : 결과 정렬 여부
    seed : 재현 가능한 랜덤 시드
    bonus_count : 보너스 번호 개수
    bonus_from_remaining : 보너스를 메인 제외 잔여풀에서 뽑을지 여부
    repeat : 추첨 반복 횟수
    return_stats : 번호 출현 통계를 함께 반환할지 여부
    """
    include = list(include or [])
    exclude = set(exclude or [])
    rng = random.Random(seed)

    if range_min > range_max:
        raise ValueError("range_min은 range_max보다 클 수 없습니다.")
    if count < 0:
        raise ValueError("count는 0 이상이어야 합니다.")
    if bonus_count < 0:
        raise ValueError("bonus_count는 0 이상이어야 합니다.")
    if repeat < 1:
        raise ValueError("repeat는 1 이상이어야 합니다.")

    # 기본 후보 풀 구성(양끝 포함)
    base_pool = list(range(range_min, range_max + 1))
    pool = [n for n in base_pool if n not in exclude]

    # include 검증
    dedup_include = []
    seen = set()
    for n in include:
        if n not in pool:
            raise ValueError(f"include 값 {n}이 후보 풀에 없습니다.")
        if n not in seen:
            dedup_include.append(n)
            seen.add(n)
    include = dedup_include

    if not overlap and len(include) > count:
        raise ValueError("include 개수가 count보다 많습니다.")

    def one_draw():
        main = include[:]
        need = count - len(main)

        if need > 0:
            if overlap:
                main.extend(rng.choices(pool, k=need))
            else:
                selectable = [n for n in pool if n not in set(main)]
                if need > len(selectable):
                    raise ValueError("중복 없이 뽑을 수 있는 번호가 부족합니다.")
                main.extend(rng.sample(selectable, k=need))

        if sort_result:
            main.sort()

        bonus = []
        if bonus_count > 0:
            if overlap:
                bonus = rng.choices(pool, k=bonus_count)
            else:
                if bonus_from_remaining:
                    remain = [n for n in pool if n not in set(main)]
                else:
                    remain = pool[:]
                if bonus_count > len(remain):
                    raise ValueError("보너스를 뽑을 수 있는 번호가 부족합니다.")
                bonus = rng.sample(remain, k=bonus_count)
            if sort_result:
                bonus.sort()

        if bonus_count > 0:
            return {"main": main, "bonus": bonus}
        return main

    def make_stats(results):
        stats_main = {}
        stats_bonus = {}

        for item in results:
            if bonus_count > 0:
                main_numbers = item["main"]
                bonus_numbers = item["bonus"]
            else:
                main_numbers = item
                bonus_numbers = []

            for n in main_numbers:
                stats_main[n] = stats_main.get(n, 0) + 1
            for n in bonus_numbers:
                stats_bonus[n] = stats_bonus.get(n, 0) + 1

        sorted_main = dict(sorted(stats_main.items()))
        sorted_bonus = dict(sorted(stats_bonus.items()))
        if bonus_count > 0:
            return {"main_counts": sorted_main, "bonus_counts": sorted_bonus}
        return {"main_counts": sorted_main}

    if repeat == 1:
        single = one_draw()
        if return_stats:
            return {"results": [single], "stats": make_stats([single])}
        return single

    results = [one_draw() for _ in range(repeat)]
    if return_stats:
        return {"results": results, "stats": make_stats(results)}
    return results


def random_Algorithm(count, range_min=1, range_max=100, overlap=True):
    # 기존 함수명 호환용 래퍼
    return draw(
        count=count,
        range_min=range_min,
        range_max=range_max,
        overlap=overlap,
    )


def main() -> None:
    # 기본 예시
    print("기본 뽑기:", draw())
    print("중복 허용:", draw(count=6, range_min=1, range_max=10, overlap=True))
    print(
        "포함/제외/보너스:",
        draw(
            count=6,
            range_min=1,
            range_max=45,
            include=[3, 11],
            exclude=[13, 17],
            bonus_count=1,
            seed=20260313,
        ),
    )
    print(
        "반복 뽑기 + 통계:",
        draw(
            count=6,
            range_min=1,
            range_max=45,
            repeat=5,
            return_stats=True,
            seed=20260313,
        ),
    )


if __name__ == "__main__":
    main()
