#pragma once

#include <string>
#include "third_party/json/json.hpp"

namespace data
{
    // JSON 유틸 모듈 (선언)
    // - manager.json, menu.json 등 리소스 JSON 입출력 함수 제공
    // - 다른 모듈(Login/Display/Shopping)에서 include하여 사용
    //
    // manager.json 예시:
    // { "managers": [ {"id":"admin","pw":"1234"}, ... ], "last_update":"YYYY-MM-DD" }
    //
    // menu.json 예시(배열 구조):
    // { "categories":[ {"name":"국","items":[{"name":"된장국","price":6000}, ...]}, ... ] }

    // JSON 타입 별칭 (nlohmann::json)
    using json = nlohmann::json;

    // ---- Json 경로 선언 위치 ----
    // 로그인 계정 정보(JSON)
    extern const std::string path_LoginIDPW;
    // 메뉴 정보(JSON)
    extern const std::string path_MenuData;

    // 샘플 관리자 JSON 생성
    json CreateSampleJson();
    // JSON 파일 저장
    bool WriteJsonFile(const std::string &path, const json &j);
    // 폴더 경로 + 파일명(.json 보정) 결합
    std::string BuildJsonPath(const std::string &path, const std::string &jsonName);
    // JSON 파일 생성(저장) 후 데이터 반환
    json CreateJson(const std::string &path, const std::string &jsonName, const json &content);
    // JSON 파일 읽기
    bool ReadJsonFile(const std::string &path, json &out);
} // namespace data
