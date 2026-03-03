#pragma once

#include <string>

namespace display_manager
{
    // 메뉴 관리 화면 실행
    // - userId: 접속 중인 관리자 ID (비밀번호 재확인용)
    void RunMenuManage(const std::string &userId);
} // namespace display_manager
