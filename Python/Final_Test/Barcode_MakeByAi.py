# 숫자(문자열) -> 바코드 패턴 매핑표
# 바코드 딕셔너리 설정
BARCODE_MAP = {
    "0": "||:::",
    "1": ":::||",
    "2": "::|:|",
    "3": "::||:",
    "4": ":|::|",
    "5": ":|:|:",
    "6": ":||::",
    "7": "|:::|",
    "8": "|::|:",
    "9": "|:|::",
}

# 바코드 패턴 -> 숫자(문자열) 역매핑표
REVERSE_MAP = {v: k for k, v in BARCODE_MAP.items()}
# 바코드 한 글자의 폭(패턴 길이)
BAR_WIDTH = 5
#-------------------------------------------------------------------
# 위는 바코드 딕셔너리 , 바코드 역매핑 딕녀너리, 바코드 길이를 선언

# 인코딩
def encode_digits(digits: str) -> str:
    """숫자 문자열을 바코드 문자열로 변환한다."""
    # 숫자만 있는지 검사
    if not digits.isdigit():
        raise ValueError("숫자만 입력하세요.")
    # 길이가 5~10자리인지 검사
    if not (5 <= len(digits) <= 10):
        raise ValueError("길이는 5~10자리여야 합니다.")
    # 각 숫자를 바코드로 바꿔서 이어붙임
    return "".join(BARCODE_MAP[d] for d in digits)

# 디코딩
def decode_barcode(barcode: str) -> str:
    """바코드 문자열을 숫자 문자열로 변환한다."""
    # 전체 길이가 5의 배수여야 정상적인 바코드 묶음
    if len(barcode) % BAR_WIDTH != 0:
        raise ValueError("바코드 길이가 올바르지 않습니다.")
    out = []  # 복호화된 숫자들을 담을 리스트
    # 5글자씩 잘라서 하나의 숫자로 복호화
    for i in range(0, len(barcode), BAR_WIDTH):
        chunk = barcode[i:i + BAR_WIDTH]
        # 정의되지 않은 패턴이면 오류
        if chunk not in REVERSE_MAP:
            raise ValueError(f"알 수 없는 패턴: {chunk}")
        out.append(REVERSE_MAP[chunk])
    # 리스트에 모인 숫자들을 하나의 문자열로 합침
    return "".join(out)


def prompt_digits() -> str:
    """조건에 맞는 숫자 입력을 받을 때까지 반복."""
    while True:
        # 입력받고 양끝 공백 제거
        s = input("5~10 자리 숫자를 입력하세요: ").strip()
        # 숫자만 있고 길이가 5~10자리면 반환
        if s.isdigit() and 5 <= len(s) <= 10:
            return s
        # 조건에 맞지 않으면 다시 입력 요청
        print("숫자만 입력하고 길이는 5~10자리여야 합니다.")


def main() -> None:
    # 1) 입력 받기
    digits = prompt_digits()
    # 2) 암호화
    encoded = encode_digits(digits)
    print("생성된 바코드 :", encoded)
    print("-" * 60)
    print("복호화 과정")
    # 3) 복호화
    decoded = decode_barcode(encoded)
    print("복호화된 숫자 :", decoded)


if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때만 main()을 호출
    main()
