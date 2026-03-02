/*
   제작 시간 : 0227_20:47
   유형 : 과제
   주제 : 키오스크 만들기 - 관리자 로그인
   설명 :
   - manager.json의 ID/PW를 읽어 로그인 입력과 비교한다.
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

using namespace std;

namespace login
{
    // 데이터 흐름:
    // - manager.json을 읽어 ID/PW 검증
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
            std::tm local_tm{};
#if defined(_WIN32)
            localtime_s(&local_tm, &now);
#else
            localtime_r(&now, &local_tm);
#endif

            std::ostringstream oss;
            oss << (local_tm.tm_year + 1900) << "_"
                << std::setw(2) << std::setfill('0') << (local_tm.tm_mon + 1) << "_"
                << std::setw(2) << std::setfill('0') << local_tm.tm_mday << "_"
                << std::setw(2) << std::setfill('0') << local_tm.tm_hour << ":"
                << std::setw(2) << std::setfill('0') << local_tm.tm_min;
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
    LoginResult Login_First()
    {
        cout << "로그인 시스템 부팅......\n";
        cout << "로그인을 시작합니다.\n";
        int failCount = 0;
        std::vector<IDPW> failedAttempts;
        while (true)
        {
            IDPW idpw;
            Login_Input(idpw);
            LoginResult result = Login_Check(idpw);

            if (result == LoginResult::Success)
                return LoginResult::Success;

            if (result == LoginResult::DataError)
                return LoginResult::DataError;

            failedAttempts.push_back(idpw);
            failCount++;
            if (failCount >= 3)
            {
                AppendLoginErrorRecord(failedAttempts);
                cout << "로그인 3회 이상 실패. 프로그램을 종료합니다.\n";
                std::exit(1);
            }
        }
        return LoginResult::Failed;
    }
    // 사용자로부터 ID/PW 입력
    void Login_Input(IDPW &idpw)
    {
        cout << "ID와 PW를 입력해주세요. \n"
             << "3번 이상 틀릴 시 프로그램이 자동 종료 및 오류 송출을 시작합니다.\n\n";
        cout << "ID : ";
        cin >> idpw.id;
        cout << "PW : ";
        cin >> idpw.pw;
    }
    // manager.json을 읽어 ID/PW 검증
    LoginResult Login_Check(const IDPW &idpw)
    {
        // const string path = "C:\\Study\\CPP\\Project_Kiosk\\Resource\\manager.json";
        const string path = data::path_LoginIDPW;
        data::json data;
        if (!data::ReadJsonFile(path, data))
        {
            cout << "로그인 데이터(JSON) 읽기 실패\n";
            return LoginResult::DataError;
        }

        if (!data.contains("managers") || !data["managers"].is_array())
        {
            cout << "로그인 데이터 형식 오류\n";
            return LoginResult::DataError;
        }

        for (const auto &item : data["managers"])
        {
            if (!item.contains("id") || !item.contains("pw"))
                continue;

            string storedId = item["id"].get<string>();
            string storedPw = item["pw"].get<string>();

            if (storedId == idpw.id)
            {
                if (storedPw == idpw.pw)
                {
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
