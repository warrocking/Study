#pragma once

#include "DataManager.h"

namespace display
{
    // 메뉴 출력 결과
    struct MenuResult
    {
        bool exitRequested; // "out" 입력 시 true
        data::json cart;    // 장바구니(JSON)
    };

    // menu.json을 읽어 화면 출력 및 입력 처리 후 결과 반환
    // - "out" 입력 시 exitRequested = true
    MenuResult RunMenu();
} // namespace display
