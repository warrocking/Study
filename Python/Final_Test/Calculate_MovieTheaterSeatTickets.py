"""
    제작 시간 : 0311_10:29
    유형 : 과제
    주제 : 영화관 좌석 티켓 계산
    문제 설명 : 
    - 행 1~12, 열 A~H까지
    - A1~12, B1~12 , C1,2 11, 12, D1,2,11,12, E1,2,11,12, F1,2,11,12-> EC 등급 좌석 : 7,000원
    - C3~10, D3~10, E3~10, F3~10-> RE 등급 좌석 : 8,000원
    - G1~12, H1~12 -> SP 등급 좌석 : 10,000원
    - 
    - 전체 좌석 배치도 출력 -> 좌석 번호 입력 -> 좌석 번호 유효 판별 -> 좌석 번호에 따른 티켓 가격 계산 -> 좌석번호와 티켓 가격 출력 -> 종료
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


seatPrice = {
    "EC" : 7000,
    "RE" : 8000,
    "SP" : 10000
}

seatList = ['EC', 'RE', 'SP']

seatConfiguration = {}
#------------------- AI 제작 -----------------------------------------
# 리스트에서 딕셔너리로 변경
def determinationOfSeatClass():
    row_labels = "ABCDEFGH"
    for y in range(1, 9):
        row_label = row_labels[y - 1]
        for x in range(1, 13):
            seat_label = f"{row_label}{x}"
            if 1 <= y <= 2:
                seatConfiguration[seat_label] = "EC"
            elif 3 <= y <= 6:
                if 1 <= x <= 2:
                    seatConfiguration[seat_label] = "EC"
                elif 3 <= x <= 10:
                    seatConfiguration[seat_label] = "RE"
                elif 11 <= x <= 12:
                    seatConfiguration[seat_label] = "EC"
            elif 7 <= y <= 8:
                seatConfiguration[seat_label] = "SP"
#------------------- AI 제작 -----------------------------------------

def main() -> None:
    # 변수 선언 및 초기화
    determinationOfSeatClass()
    print()
    print("좌석 가격 = ", end = " ")
    for key in seatPrice:
        print(key, ":", seatPrice[key], end = " ")
    
    print()
    # 좌석 출력 (행 A~H, 열 1~12 형식) - 정렬 폭을 일정하게 맞춤
    
    #------------------- AI 제작 -----------------------------------------
    cell_width = 3  # 좌석 코드/번호를 표시할 칸의 폭
    header_numbers = " ".join(f"{n:>{cell_width}}" for n in range(1, 13))
    row_prefix = "A | "  # 행 라벨 출력 폭 기준

    print(" " * len(row_prefix) + header_numbers)
    print(" " * len(row_prefix) + "-" * len(header_numbers))

    row_labels = "ABCDEFGH"
    for row in range(8):
        row_label = row_labels[row]
        row_seats = " ".join(
            f"{seatConfiguration[f'{row_label}{col}']:>{cell_width}}" for col in range(1, 13)
        )
        print(f"{row_label} | {row_seats}")
    #------------------- AI 제작 -----------------------------------------


    # 좌석 선택하기
    list_selectedSeat = []
    while True:
        selectedSeat = input("원하는 좌석 입력(좌석 선택이 끝날 시 '0' 입력) : ").strip().upper()
        if(selectedSeat == "0"):
            if(len(list_selectedSeat)!=0):
                print("선택한 좌석은 {} 입니다.".format(list_selectedSeat))
                break
            else:
                print("선택된 좌석이 없습니다. 다시 입력해주세요.\n")
            
        elif(selectedSeat not in seatConfiguration):#잘못된 입력은 제외 시키기
            
            pass
        else:
            list_selectedSeat.append(selectedSeat)
    
    # 좌석에 맞게 가격 계산해서 출력하기
    print("선택한 각 좌석의 가격은 다음과 같습니다.")
    totalPrice =0
    for i in range(0, len(list_selectedSeat)):
        print(list_selectedSeat[i],":",seatPrice[seatConfiguration[list_selectedSeat[i]]])
        totalPrice += seatPrice[seatConfiguration[list_selectedSeat[i]]]
    
    print("총 가격 : {}원".format(totalPrice))


if __name__ == "__main__":
    main()
