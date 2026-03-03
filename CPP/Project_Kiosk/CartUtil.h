#pragma once

#include "DataManager.h"

namespace cartutil
{
    // 장바구니 총합 계산
    inline int CalcCartTotal(const data::json &cart)
    {
        int sum = 0;
        if (!cart.contains("categories") || !cart["categories"].is_array())
            return 0;
        for (const auto &cat : cart["categories"])
        {
            if (!cat.contains("items") || !cat["items"].is_array())
                continue;
            for (const auto &it : cat["items"])
            {
                sum += it.value("total", 0);
            }
        }
        return sum;
    }
} // namespace cartutil
