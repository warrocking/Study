"""
Data_AI.py

이 파일의 목적:
1) 데이터 입출력 API를 하나로 통일한다.
   - create(...)
   - exists(...)
   - save(...)
   - load(...)
2) 저장 형식(JSON/Excel)을 옵션 한 개로 전환한다.
   - backend="json"
   - backend="excel"
3) 호출 코드를 단순하게 유지한다.
   - 호출부는 백엔드별 상세 로직을 몰라도 된다.

동작 흐름(쉽게):
1) 코드에서 DataAI(backend="json" 또는 "excel")를 만든다.
2) DataAI가 내부적으로 실제 저장소 객체를 선택한다.
   - JsonStore 또는 ExcelStore
3) save/load/create/exists 호출은 선택된 저장소로 전달된다.
4) 저장소 클래스가 경로 계산, 파일 생성, 읽기/쓰기를 수행한다.
5) 보조 기능:
   - specific_data: 로드 데이터 중 특정 위치만 추출
   - expected_type: 반환 형식을 list/dict/str/float로 맞춤

이 구조의 장점:
- JSON/Excel 모두 같은 메서드 이름으로 사용 가능
- 유지보수/확장 용이
- 화면/로또 로직과 저장 형식 로직을 분리할 수 있음
"""

import json
import os
from datetime import datetime


def _pick_specific(data, specific_data):
    # 보조 함수: 로드된 데이터에서 필요한 부분만 추출
    # specific_data가 None이면 전체 데이터를 그대로 반환
    """중첩 데이터에서 key/index/path 기준으로 특정 데이터 추출.

    지원 형태:
    - dict 키: "history"
    - list 인덱스: 0
    - 경로(list/tuple): ["history", 0, "numbers"]
    """
    if specific_data is None:
        return data

    if isinstance(specific_data, (list, tuple)):
        current = data
        for key in specific_data:
            if isinstance(current, dict) and key in current:
                current = current[key]
                continue
            if isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
                current = current[key]
                continue
            return None
        return current

    if isinstance(data, dict):
        return data.get(specific_data)

    if isinstance(data, list) and isinstance(specific_data, int):
        if 0 <= specific_data < len(data):
            return data[specific_data]
        return None

    return None


def _cast_expected(data, expected_type):
    # 보조 함수: 반환 타입을 정리해서 호출 코드를 단순하게 유지
    """반환 형식을 일관되게 맞춘다."""
    if expected_type is None:
        return data

    if expected_type is list:
        if isinstance(data, list):
            return data
        if data is None:
            return []
        return [data]

    if expected_type is dict:
        if isinstance(data, dict):
            return data
        if data is None:
            return {}
        return {"value": data}

    if expected_type is str:
        if data is None:
            return ""
        return str(data)

    if expected_type is float:
        try:
            return float(data)
        except (TypeError, ValueError):
            return None

    return data


class JsonStore:
    # JSON 파일 전용 저장소 구현
    # 경로 계산, 생성/존재 확인/저장/로드 담당
    """JSON 백엔드 구현."""

    def __init__(self, base_folder="Resource"):
        # 호출 시 file_path를 직접 주지 않으면 base_folder를 사용
        self.base_folder = base_folder

    def _resolve_path(self, file_name, file_folder=None, file_path=None):
        # 우선순위:
        # 1) file_path 직접 전달
        # 2) base_folder + file_name 조합
        if file_path is not None:
            abs_path = os.path.abspath(file_path)
            root, ext = os.path.splitext(abs_path)
            if ext:
                # 확장자가 있으면 파일 경로로 간주
                return abs_path
            # 확장자가 없으면 폴더 경로로 간주하고 file_name을 붙임
            return os.path.join(abs_path, file_name)

        folder = self.base_folder if file_folder is None else file_folder
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", folder, file_name)
        )

    def exists(self, file_name, file_folder=None, file_path=None):
        # 대상 파일 존재 여부 확인
        path = self._resolve_path(file_name, file_folder, file_path)
        return os.path.isfile(path)

    def create(self, file_name, default_data=None, file_folder=None, file_path=None):
        # 파일이 없을 때만 생성
        # 기본 생성 데이터는 [] (append/read 시작이 쉬움)
        path = self._resolve_path(file_name, file_folder, file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if default_data is None:
            default_data = []
        if not os.path.isfile(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
        return path

    def save(
        self,
        data,
        file_name,
        file_folder=None,
        file_path=None,
        mode="overwrite",
        history_key="history",
    ):
        # 저장 모드:
        # - overwrite: 파일 전체 덮어쓰기
        # - append: 기존 구조에 데이터 추가
        path = self._resolve_path(file_name, file_folder, file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if mode == "append":
            if not os.path.isfile(path):
                current = []
            else:
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        current = json.load(f)
                    except json.JSONDecodeError:
                        # JSON이 깨졌으면 빈 리스트로 복구 처리
                        current = []

            if isinstance(current, list):
                # 흔한 패턴: 최상위 리스트에 레코드 누적
                current.append(data)
                out = current
            elif isinstance(current, dict):
                # dict 패턴: current[history_key] 리스트에 누적
                if history_key not in current or not isinstance(current.get(history_key), list):
                    current[history_key] = []
                current[history_key].append(data)
                out = current
            else:
                # 예외 타입이면 기존값+신규값을 리스트로 보관
                out = [current, data]
        else:
            # overwrite 모드
            out = data

        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        return path

    def load(
        self,
        file_name,
        expected_type=list,
        specific_data=None,
        file_folder=None,
        file_path=None,
        auto_create=True,
    ):
        # 로드 시 자동 생성(auto_create) 옵션 지원
        path = self._resolve_path(file_name, file_folder, file_path)

        if not os.path.isfile(path):
            if auto_create:
                # 파일이 없으면 빈 파일 자동 생성
                self.create(file_name, default_data=[], file_folder=file_folder, file_path=file_path)
            else:
                return _cast_expected(None, expected_type)

        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 빈 리스트로 처리
                data = []

        # 필요한 위치(specific_data)만 추출 가능
        data = _pick_specific(data, specific_data)
        # 반환 형식(expected_type) 맞춤
        return _cast_expected(data, expected_type)


class ExcelStore:
    # Excel 파일 전용 저장소 구현
    # 내부적으로 pandas/openpyxl 사용
    """Excel 백엔드 구현 (pandas 사용)."""

    def __init__(self, base_folder="Resource"):
        self.base_folder = base_folder

    def _require_pandas(self):
        # 지연 import: Excel 기능을 쓸 때만 pandas를 요구
        try:
            import pandas as pd  # type: ignore
            return pd
        except Exception as exc:  # pragma: no cover
            raise ImportError("Excel backend needs pandas + openpyxl.") from exc

    def _resolve_path(self, file_name, file_folder=None, file_path=None):
        # JsonStore와 동일한 경로 규칙
        if file_path is not None:
            abs_path = os.path.abspath(file_path)
            root, ext = os.path.splitext(abs_path)
            if ext:
                return abs_path
            return os.path.join(abs_path, file_name)

        folder = self.base_folder if file_folder is None else file_folder
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", folder, file_name)
        )

    def exists(self, file_name, file_folder=None, file_path=None):
        path = self._resolve_path(file_name, file_folder, file_path)
        return os.path.isfile(path)

    def create(self, file_name, default_data=None, file_folder=None, file_path=None, sheet_name="Sheet1"):
        # 빈 파일 또는 초기 데이터 Excel 파일 생성
        pd = self._require_pandas()
        path = self._resolve_path(file_name, file_folder, file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.isfile(path):
            if default_data is None:
                df = pd.DataFrame()
            else:
                df = pd.DataFrame(default_data)
            df.to_excel(path, index=False, sheet_name=sheet_name)
        return path

    def save(self, data, file_name, file_folder=None, file_path=None, sheet_name="Sheet1"):
        # 데이터를 DataFrame으로 변환해 Excel에 저장
        pd = self._require_pandas()
        path = self._resolve_path(file_name, file_folder, file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df = pd.DataFrame(data)
        df.to_excel(path, index=False, sheet_name=sheet_name)
        return path

    def load(
        self,
        file_name,
        expected_type=list,
        specific_data=None,
        file_folder=None,
        file_path=None,
        sheet_name="Sheet1",
        auto_create=True,
    ):
        # Excel 로드 후 list[dict] 구조로 변환
        pd = self._require_pandas()
        path = self._resolve_path(file_name, file_folder, file_path)

        if not os.path.isfile(path):
            if auto_create:
                self.create(file_name, default_data=[], file_folder=file_folder, file_path=file_path, sheet_name=sheet_name)
            else:
                return _cast_expected(None, expected_type)

        df = pd.read_excel(path, sheet_name=sheet_name)
        # 테이블 행을 일반 파이썬 구조로 변환
        data = df.to_dict(orient="records")
        data = _pick_specific(data, specific_data)
        return _cast_expected(data, expected_type)


class DataAI:
    # 프로젝트 호출부에서 사용하는 공통 창구(Facade)
    # 호출 코드는 한 API만 쓰고, 백엔드 상세는 숨긴다.
    """JSON/Excel 공통 메서드명을 제공하는 퍼사드."""

    def __init__(self, backend="json", base_folder="Resource"):
        self.backend = backend.lower()
        if self.backend == "json":
            self.store = JsonStore(base_folder=base_folder)
        elif self.backend == "excel":
            self.store = ExcelStore(base_folder=base_folder)
        else:
            raise ValueError("backend must be 'json' or 'excel'")

    def create(self, file_name, **kwargs):
        # 선택된 백엔드로 호출 전달
        return self.store.create(file_name=file_name, **kwargs)

    def exists(self, file_name, **kwargs):
        # 선택된 백엔드로 호출 전달
        return self.store.exists(file_name=file_name, **kwargs)

    def save(self, data, file_name, **kwargs):
        # 선택된 백엔드로 호출 전달
        return self.store.save(data=data, file_name=file_name, **kwargs)

    def load(self, file_name, expected_type=list, specific_data=None, **kwargs):
        # 선택된 백엔드로 호출 전달
        return self.store.load(
            file_name=file_name,
            expected_type=expected_type,
            specific_data=specific_data,
            **kwargs,
        )


def main():
    # 실행 예시:
    # 1) JSON 백엔드 퍼사드 생성
    # 2) 파일 생성(없을 때만)
    # 3) 데이터 1건 append
    # 4) 로드 후 출력
    now_text = datetime.now().isoformat(timespec="seconds")
    db = DataAI(backend="json", base_folder="Resource")
    db.create("lotto_history.json", default_data=[])
    db.save(
        {"saved_at": now_text, "numbers": [1, 2, 3, 4, 5, 6], "bonus": 7},
        "lotto_history.json",
        mode="append",
    )
    print(db.load("lotto_history.json", expected_type=list))


if __name__ == "__main__":
    main()
