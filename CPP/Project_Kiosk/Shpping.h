#pragma once

#include "DataManager.h"

namespace shopping
{
    // Display에서 생성한 장바구니(JSON)를 받아 결제 단계로 전달
    // cart 구조:
    // { "categories":[ {"name":"국","items":[{"name":"된장국","qty":2,"total":12000}, ...]}, ... ] }
    // 조건 통과 시 true, 제한 위반 시 false 반환
    bool RunShopping(data::json &cart);
} // namespace shopping
