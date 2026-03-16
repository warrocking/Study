"""
    제작 시간 : 0313_22:29
    유형 : 과제
    주제 : 
    문제 설명 : 
    - 
"""

# 기본 모듈
import sys
import json
import os
from datetime import datetime

class _Json:
    # 변수 지정
    file_folder = "Resource"
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", file_folder))

    # 함수 지정
    # @staticmethod # -> AI추천. class 내에서 변수, 함수, 데이터 등을 가져다 쓰지 않는 경우 붙여서 프로그램이 인식하는게 좋음. 목적은 주석과 같긴함.
    def _check(file_name, file_folder=None, file_path=None):
        # file_folder를 입력 안하면 어차피 file_path도 없으니까 file_path 먼저 확인
        if file_path is not None:#파일 경로 확인
            target_path = os.path.abspath(file_path)
            # 파일 경로가 아니라 폴더 경로가 들어온 경우 file_name 붙이기
            root, ext = os.path.splitext(target_path)
            if not ext:
                target_path = os.path.join(target_path, file_name)
        else:#파일 경로 없으면
            if file_folder is not None:#폴더 확인하기
                base_folder = file_folder
            else:
                base_folder = _Json.file_folder
        #------------ 폴더와 경로 확인했으니 최종 경로 정하기 -----------
            #abspath => absolute(절대) path(경로) , 즉 경로 확정적으로 만들어주기
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", base_folder))
            # 상대경로가 아니라 절대경로를 만들어서 쓰는 이유는 어차피 코드를 나중에 프로젝트 할 곳에 넣어도,
            # 나중에 실행파일 위치가 다르면 문제가 생겨서 혹시 모를 이유 방지로 사용
            # 상대 경로 쓰다가 해당 내용을 AI에게 듣고 절대로 수정함.
            target_path = os.path.join(base_path, file_name)
        return os.path.isfile(target_path)# 파일 존재 여부만 bool로 반환

    def _Load(file_name, file_folder=None, file_path=None):
        # file_name : 파일이름
        # expected_type : 파일 형태 (기본은 list, list가 가장 일반적으로 쓰는중)
        # specific_data : 파일 안의 특정 데이터 읽기
        # file_folder, path 는 check랑 같음
        if _Json._check(file_name, file_folder, file_path):#파일이 있을때
            list_data = []
            with open(file_path, "r", encoding="utf-8") as f:
                list_data = json.load(f)
            return list_data
            
        else: # 파일이 없을떄
            return None
    

def main() -> None:
    print("[기본 호출]")
    print(_Json._check("lotto_history.json"))
    print()

    print("[file_folder 전달]")
    print(_Json._check("lotto_history.json", file_folder="Data"))
    print()

    print("[file_path 전달]")
    print(_Json._check("lotto_history.json", file_path="C:\\Study\\Python\\Project_Lotto\\Data\\lotto_history.json"))
    pass


if __name__ == "__main__":
    main()
