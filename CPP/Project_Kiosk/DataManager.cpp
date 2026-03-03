/*
   제작 시간 : 0227_20:49
   유형 : 과제
   주제 : 키오스크 만들기 - JSON 데이터 관리
   설명 :
   - access_control.json, menu.json, PaymentReceipt.json 등 JSON 파일을 읽고 쓴다.
   - 경로/파일명을 결합하여 .json 확장자를 보정하는 유틸을 제공한다.
   - JSON 생성/저장, 샘플 데이터 생성 등 공통 데이터 작업을 담당한다.
*/

#include <fstream> // 파일 입출력 (std::ifstream, std::ofstream)
#include <string>  // 문자열 처리 (std::string)

#include "DataManager.h" // JSON 타입/선언 (data::json, ReadJsonFile, WriteJsonFile)

namespace data
{
    // 프로젝트 리소스 경로(JSON 위치)
    const std::string path_AccessControl = "C:\\Study\\CPP\\Project_Kiosk\\Resource\\access_control.json";
    const std::string path_MenuData = "C:\\Study\\CPP\\Project_Kiosk\\Resource\\menu.json";

    // 권한 샘플 JSON 생성 (초기 세팅용)
    json CreateSampleJson()
    {
        json j;
        j["users"] = json::array({{{"id", "master"}, {"pw", "0000"}, {"role", "master"}},
                                  {{"id", "manager"}, {"pw", "1234"}, {"role", "manager"}},
                                  {{"id", "staff"}, {"pw", "1111"}, {"role", "staff"}},
                                  {{"id", "guest"}, {"pw", "9999"}, {"role", "guest"}}});
        j["roles"] = {
            {"master", {"menu_manage", "sales_view", "sales_manage", "user_manage", "sales_start", "system_manage"}},
            {"manager", {"menu_manage", "sales_view", "sales_manage", "user_manage", "sales_start", "system_manage"}},
            {"staff", {"sales_start", "system_manage"}},
            {"guest", {"sales_view", "system_manage"}}};
        j["last_update"] = "2026-03-03";
        return j;
    }

    // JSON 파일 저장
    bool WriteJsonFile(const std::string &path, const json &j)
    {
        std::ofstream out(path);
        if (!out)
            return false;
        out << j.dump(2);
        return true;
    }

    // 폴더 경로 + 파일명 결합 (확장자 보정 포함)
    std::string BuildJsonPath(const std::string &path, const std::string &jsonName)
    {
        std::string fullPath = path;
        if (!fullPath.empty())
        {
            char last = fullPath.back();
            if (last != '\\' && last != '/')
                fullPath += '\\';
        }

        std::string name = jsonName;
        const std::string ext = ".json";
        if (name.size() < ext.size() || name.substr(name.size() - ext.size()) != ext)
            name += ext;

        return fullPath + name;
    }

    // JSON 생성 + 저장 (콘텐츠 반환)
    json CreateJson(const std::string &path, const std::string &jsonName, const json &content)
    {
        const std::string fullPath = BuildJsonPath(path, jsonName);
        WriteJsonFile(fullPath, content);
        return content;
    }

    // JSON 파일 읽기
    bool ReadJsonFile(const std::string &path, json &out)
    {
        std::ifstream in(path);
        if (!in)
            return false;
        try
        {
            in >> out;
            return true;
        }
        catch (...)
        {
            return false;
        }
    }
} // namespace data
