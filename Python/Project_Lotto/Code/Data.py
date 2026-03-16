"""
    제작 시간 : 0313_12:14
    유형 : 과제
    주제 : 데이터 저장, 출력, 변경 등의 역할
    문제 설명 : 
    - json의 데이터 저장 및 출력
    
    - 주 역할
        - 뽑기 이후 Json으로 무조건 데이터 저장해놓기
        - 뽑기 이후 결과 확인을 할때 
"""

# 기본 모듈
import json
import os
from datetime import datetime
# 추가 모듈 (필요 시 주석 해제)
# import math
# import itertools
# import collections


# - __file__ : 현재 파일(Data.py)의 경로
# - os.path.dirname(__file__) : 현재 파일이 있는 폴더
# - "..", "Data" : 상위 폴더(Project_Lotto) 아래의 Data 폴더
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Data"))

# 기본 저장 파일 경로
# - 별도 경로를 주지 않으면 이 파일에 저장/로드한다.
DEFAULT_JSON_PATH = os.path.join(DATA_DIR, "lotto_history.json")


def _normalize_root(data):
    # 저장 파일의 최상위 구조를 항상 {"history": [...]} 형태로 맞춘다.
    # 이유:
    # - 저장 포맷이 섞이면(리스트/딕셔너리/단일값) 이후 코드가 복잡해진다.
    # - 그래서 어떤 입력이 와도 history 리스트 기반 구조로 통일한다.
    if isinstance(data, dict) and isinstance(data.get("history"), list):
        # 이미 원하는 구조면 그대로 사용
        return data
    if isinstance(data, list):
        # 리스트만 있으면 history로 감싸서 통일
        return {"history": data}
    if data is None:
        # 파일이 비어 있거나 없으면 빈 history로 시작
        return {"history": []}
    # 단일 값/기타 타입도 history에 1개 넣어 통일
    return {"history": [data]}


def make_Json(data=None, **extra):  # 받은 데이터를 Json 데이터로 만들기
    # 저장 시각을 기본 필드로 먼저 넣는다.
    # 예: "2026-03-13T22:09:43"
    record = {
        "saved_at": datetime.now().isoformat(timespec="seconds")
    }

    # data 타입에 따라 record 형태를 자동으로 맞춘다.
    # 1) dict  -> 필드를 그대로 병합
    # 2) list/tuple -> "numbers" 필드에 저장
    # 3) 그 외 단일값 -> "value" 필드에 저장
    if isinstance(data, dict):
        record.update(data)
    elif isinstance(data, (list, tuple)):
        record["numbers"] = list(data)
    elif data is not None:
        record["value"] = data

    # extra로 받은 추가 키워드 인자들을 병합
    # 예: save_Json(..., ticket_count=5, paid=25000)
    if extra:
        record.update(extra)

    # 최종 1건 레코드 반환
    return record


def save_Json(data=None, file_path=DEFAULT_JSON_PATH, **extra):
    # JSON 데이터 저장 함수
    # 흐름:
    # 1) 폴더 보장
    # 2) 기존 파일 로드
    # 3) 루트 구조 통일
    # 4) 새 레코드 생성
    # 5) history에 append
    # 6) 파일에 다시 쓰기

    # 저장 폴더가 없으면 자동 생성
    if not os.path.isdir(os.path.dirname(file_path)):# isdir = is Dirc
        os.makedirs(os.path.dirname(file_path))

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 기존 데이터 불러오기(None 가능)
    current = load_Json(file_path)
    # 저장 구조 통일
    root = _normalize_root(current)

    # 이번에 저장할 레코드 1건 만들기
    record = make_Json(data, **extra)
    # history 리스트에 누적 추가
    root["history"].append(record)

    # 파일에 UTF-8로 저장
    # ensure_ascii=False : 한글이 \uXXXX로 깨지지 않게 저장
    # indent=2 : 사람이 읽기 좋은 들여쓰기
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=1)

    # 저장된 레코드를 바로 반환(호출 측에서 로그/확인 가능)
    return record


def check_Json(file_path=DEFAULT_JSON_PATH):  # Json 데이터 있는지 체크하기
    # 파일이 존재하고, 크기가 0보다 크면 True
    # (파일은 있는데 빈 파일인 경우 False)
    return os.path.isfile(file_path) and os.path.getsize(file_path) > 0


def load_Json(file_path=DEFAULT_JSON_PATH):  # Json 데이터 불러오기
    # check_Json으로 데이터 있는지 확인
    # 없으면 None 반환
    # 있으면 데이터 불러오기
    if not check_Json(file_path):
        return None

    try:
        # 정상 파일이면 JSON 파싱 결과(보통 dict)를 반환
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # 파일이 깨졌거나 읽기 실패 시 None 반환
        return None


def main() -> None:
    # 아래는 Data.py 단독 실행 시 동작 확인용 샘플 코드
    # (실제 프로젝트에서는 Display.py 등에서 save_Json/load_Json을 호출)
    sample_record = save_Json(
        data={"numbers": [1, 2, 3, 4, 5, 6], "bonus": 7},
        note="sample",
    )
    print("저장 완료:", sample_record)
    print("파일 존재:", check_Json())
    print("불러온 데이터:", load_Json())


if __name__ == "__main__":
    main()
