#pragma once

#include "DataManager.h"

namespace payment
{
    // 결제 결과
    struct ReceiptResult
    {
        bool success;        // 결제 성공 여부
        data::json receipt;  // 결제 영수증 JSON
        int finalAmount;     // 최종 결제 금액
    };

    // cart를 받아 결제 처리 후 영수증 반환
    // - nextCount: 누적 결제 횟수(이번 결제 번호)
    ReceiptResult ProcessPayment(const data::json &cart, int nextCount);
} // namespace payment
