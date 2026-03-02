#pragma once

#include <string>

namespace login
{
    // 로그인 입력 데이터
    struct IDPW
    {
        std::string id;
        std::string pw;
    };

    // 로그인 처리 결과
    enum class LoginResult
    {
        Success,
        Failed,
        DataError
    };

    // 로그인 흐름 시작(3회 실패 시 오류 기록)
    LoginResult Login_First();
    // ID/PW 입력
    void Login_Input(IDPW &idpw);
    // JSON 데이터 기반 로그인 검증
    LoginResult Login_Check(const IDPW &idpw);
} // namespace login
