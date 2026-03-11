"""
    제작 시간 : 0311
    유형 : 과제 (개선 버전)
    주제 : 영화관 좌석 티켓 계산
    문제 설명 :
    - 행 A~H, 열 1~12
    - 좌석 등급 규칙에 따라 좌석 배치도 출력
    - 좌석 번호 입력 -> 유효성 검사 -> 좌석 가격 계산 -> 결과 출력
"""

# 기본 모듈
import sys

# 좌석 등급별 가격
PRICE_BY_GRADE = {
    "EC": 7000,
    "RE": 8000,
    "SP": 10000,
}

# 좌석 행/열 정의
ROWS = "ABCDEFGH"
COLS = range(1, 13)


def grade_for_seat(row_index: int, col: int) -> str:
    """좌석 위치(행 인덱스, 열 번호)에 따른 등급을 반환한다."""
    if 1 <= row_index <= 2:
        return "EC"
    if 3 <= row_index <= 6:
        if 1 <= col <= 2 or 11 <= col <= 12:
            return "EC"
        return "RE"
    return "SP"  # 7~8행


def build_seat_map() -> dict[str, str]:
    """좌석 번호(A1~H12) -> 등급(EC/RE/SP) 매핑을 생성한다."""
    seat_map: dict[str, str] = {}
    for row_index, row_label in enumerate(ROWS, start=1):
        for col in COLS:
            seat_label = f"{row_label}{col}"
            seat_map[seat_label] = grade_for_seat(row_index, col)
    return seat_map


def print_price_table() -> None:
    """좌석 등급과 가격을 출력한다."""
    print("좌석 가격 =", end=" ")
    for grade, price in PRICE_BY_GRADE.items():
        print(f"{grade}: {price:,}원", end=" ")
    print()


def print_seat_map(seat_map: dict[str, str]) -> None:
    """좌석 배치도를 정렬해서 출력한다."""
    cell_width = 3  # 좌석 코드/번호 표기 폭
    header_numbers = " ".join(f"{n:>{cell_width}}" for n in COLS)
    row_prefix = "A | "

    print(" " * len(row_prefix) + header_numbers)
    print(" " * len(row_prefix) + "-" * len(header_numbers))

    for row_label in ROWS:
        row_seats = " ".join(
            f"{seat_map[f'{row_label}{col}']:>{cell_width}}" for col in COLS
        )
        print(f"{row_label} | {row_seats}")


def normalize_seat_input(value: str) -> str:
    """입력 문자열을 좌석 형식으로 정규화한다."""
    return value.strip().upper()


def prompt_seats(seat_map: dict[str, str]) -> list[str]:
    """좌석을 반복 입력 받아 유효한 좌석만 리스트로 반환한다."""
    selected: list[str] = []
    while True:
        seat = normalize_seat_input(
            input("원하는 좌석 입력(끝내려면 0): ")
        )
        if seat == "0":
            break
        if seat not in seat_map:
            print("존재하지 않는 좌석입니다. 예: A1, H12")
            continue
        if seat in selected:
            print("이미 선택한 좌석입니다.")
            continue
        selected.append(seat)
    return selected


def print_receipt(selected: list[str], seat_map: dict[str, str]) -> None:
    """선택한 좌석 목록과 총액을 출력한다."""
    if not selected:
        print("선택한 좌석이 없습니다.")
        return

    total = 0
    print("선택한 좌석:")
    for seat in selected:
        grade = seat_map[seat]
        price = PRICE_BY_GRADE[grade]
        total += price
        print(f"- {seat} ({grade}) : {price:,}원")
    print(f"총액 : {total:,}원")


def main() -> None:
    seat_map = build_seat_map()
    print_price_table()
    print()
    print_seat_map(seat_map)
    print()
    selected = prompt_seats(seat_map)
    print()
    print_receipt(selected, seat_map)


if __name__ == "__main__":
    main()
