/*
   제작 시간 : 0227_20:47
   유형 : 과제
   주제 : 키오스크 만들기 - 관리자 로그인
   설명 :
   - access_control.json의 ID/PW를 읽어 로그인 입력과 비교한다.
   - 로그인 성공 시 역할(role)과 권한 목록(permissions)을 함께 반환한다.
   - 실패 시 횟수를 누적하며, 3회 실패하면 LoginError.json에 기록 후 종료한다.
   - LoginError.json에는 실패 시간과 시도한 ID/PW 목록을 누적 저장한다.
*/

#include <iostream> // 콘솔 입출력 (std::cout, std::cin)
#include <ctime>    // 시간 처리 (std::time, localtime_s/localtime_r)
#include <cstdlib>  // 강제 종료 (std::exit)
#include <vector>   // 실패 기록 저장 (std::vector)
#include <sstream>  // 문자열 구성 (std::ostringstream)
#include <iomanip>  // 출력 포맷 (std::setw, std::setfill)

#include "Login.h"       // 로그인 구조체/열거형 (IDPW, LoginResult)
#include "DataManager.h" // JSON 읽기/쓰기 (data::ReadJsonFile, WriteJsonFile)
#include "ConsoleUtil.h" // 입력 유틸 (ReadMaskedInput, ReadLineStrict)

using namespace std;

namespace login
{
    // 데이터 흐름:
    // - access_control.json을 읽어 ID/PW 검증 및 권한 로드
    // - 3회 실패 시 LoginError.json에 시간/시도 기록 누적
    //
    // LoginError.json 예시:
    // { "errors":[ { "time":"YYYY_MM_DD_HH:MM", "attempts":[{"id":"","pw":""}, ...] } ] }

    namespace
    {
        // 로그인 실패 기록용 타임스탬프 (YYYY_MM_DD_HH:MM)
        std::string BuildLoginErrorTimestamp()
        {
            std::time_t now = std::time(nullptr);
            std::tm localTm{};

#if defined(_WIN32) // 실행 환경이 윈도우 일떄, 아닐떄의 차이에 맞춰 개발함.
            localtime_s(&localTm, &now);
#else
            localtime_r(&now, &localTm);
#endif

            std::ostringstream oss;
            // 2026년 기준 localTm.tm_year = 126; 즉, 1900을 더해줘야함.             // 표기과정
            oss << (localTm.tm_year + 1900) << "_"                                  // 2026_
                << std::setw(2) << std::setfill('0') << (localTm.tm_mon + 1) << "_" // 2026_03_
                << std::setw(2) << std::setfill('0') << localTm.tm_mday << "_"      // 2026_03_03_
                << std::setw(2) << std::setfill('0') << localTm.tm_hour << ":"      // 2026_03_03_10:
                << std::setw(2) << std::setfill('0') << localTm.tm_min;             // 2026_03_03_10:30
            return oss.str();
        }

        // 3회 실패 기록(시간 + 시도한 ID/PW)
        data::json BuildLoginErrorRecord(const std::vector<IDPW> &attempts)
        {
            data::json record;
            record["time"] = BuildLoginErrorTimestamp();
            record["attempts"] = data::json::array();
            for (const auto &a : attempts)
            {
                record["attempts"].push_back({{"id", a.id}, {"pw", a.pw}});
            }
            return record;
        }

        // LoginError.json에 누적 기록 추가
        void AppendLoginErrorRecord(const std::vector<IDPW> &attempts)
        {
            const string resourcePath = "C:\\Study\\CPP\\Project_Kiosk\\Resource";
            const string fullPath = data::BuildJsonPath(resourcePath, "LoginError.json");

            data::json root;
            if (!data::ReadJsonFile(fullPath, root) || !root.contains("errors") || !root["errors"].is_array())
            {
                root = data::json::object();
                root["errors"] = data::json::array();
            }

            root["errors"].push_back(BuildLoginErrorRecord(attempts));
            data::WriteJsonFile(fullPath, root);
        }
    } // namespace

    // 로그인 전체 흐름: 입력 -> 검증 -> 실패 누적 -> 3회 실패시 기록 후 종료
    AuthInfo Login_First() // 반환종류 : Success, Failed, DataError + 권한 정보
    {
        cout << "로그인 시스템 부팅......\n";
        cout << "로그인을 시작합니다.\n";
        int failCount = 0;
        std::vector<IDPW> failedAttempts;
        while (true)
        {
            IDPW idpw;
            Login_Input(idpw);
            std::string role;
            std::vector<std::string> perms;
            LoginResult result = Login_Check(idpw, role, perms); // Json 데이터와의 비교 후 로그인 결과 반환

            if (result == LoginResult::Success) // 로그인 성공 시
                return {LoginResult::Success, idpw.id, role, perms};

            if (result == LoginResult::DataError) // 로그인 데이터 '파일'이 문제 시 반환
                return {LoginResult::DataError, "", "", {}};

            failedAttempts.push_back(idpw);
            failCount++;
            if (failCount >= 3)
            {
                AppendLoginErrorRecord(failedAttempts);
                cout << "로그인 3회 이상 실패. 프로그램을 종료합니다.\n";
                std::exit(1); // 강제 종료 (로그인 실패 시 프로그램이 더 이상 진행되지 않도록)
            }
        }
        return {LoginResult::Failed, "", "", {}};
    }
    // 사용자로부터 ID/PW 입력
    void Login_Input(IDPW &idpw)
    {
        cout << "ID와 PW를 입력해주세요. \n"
             << "3번 이상 틀릴 시 프로그램이 자동 종료 및 오류 송출을 시작합니다.\n\n";
        cout << "ID : ";
        while (!ReadLineStrict(idpw.id))
        {
            cout << "ID : ";
        }
        cout << "PW : ";
        do
        {
            idpw.pw = ReadMaskedInput(0, false);
        } while (idpw.pw.empty());
    }
    // access_control.json을 읽어 ID/PW 검증 및 권한 로드
    LoginResult Login_Check(const IDPW &idpw, std::string &outRole, std::vector<std::string> &outPerms)
    {
        const string path = data::path_AccessControl;
        data::json data;
        if (!data::ReadJsonFile(path, data))
        {
            cout << "로그인 데이터(JSON) 읽기 실패\n";
            return LoginResult::DataError;
        }

        if (!data.contains("users") || !data["users"].is_array())
        {
            cout << "로그인 데이터 형식 오류\n";
            return LoginResult::DataError;
        }

        for (const auto &item : data["users"])
        {
            if (!item.contains("id") || !item.contains("pw"))
                continue;

            string storedId = item["id"].get<string>();
            string storedPw = item["pw"].get<string>();

            if (storedId == idpw.id)
            {
                if (storedPw == idpw.pw)
                {
                    outRole = item.value("role", "");
                    if (outRole.empty())
                    {
                        cout << "권한 정보(역할) 누락\n";
                        return LoginResult::DataError;
                    }
                    if (!data.contains("roles") || !data["roles"].contains(outRole) || !data["roles"][outRole].is_array())
                    {
                        cout << "권한 정보(roles) 형식 오류\n";
                        return LoginResult::DataError;
                    }

                    outPerms.clear();
                    for (const auto &p : data["roles"][outRole])
                    {
                        if (p.is_string())
                            outPerms.push_back(p.get<string>());
                    }

                    cout << "로그인 성공\n";
                    return LoginResult::Success;
                }
                else
                {
                    cout << "비밀번호가 틀렸습니다.\n";
                    return LoginResult::Failed;
                }
            }
        }

        cout << "아이디가 존재하지 않습니다.\n";
        return LoginResult::Failed;
    }
} // namespace login
