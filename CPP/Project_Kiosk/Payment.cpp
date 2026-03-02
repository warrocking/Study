/*
   제작 시간 : 0227_20:44
   유형 : 과제
   주제 : 키오스크 만들기 - 결제 시스템
   설명 :
   - Display/Shopping에서 전달된 장바구니를 출력하고 총액을 계산한다.
   - 카드 결제는 4자리 입력 → 카드사 판별 → 결제 확인(Y/N) 순서로 진행한다.
   - 현금 결제는 10% 할인 후, 누적 입금 방식으로 잔액을 계산하고 거스름돈을 출력한다.
   - 결제 완료 시 영수증 JSON을 생성하고 10초 동안 영수증 화면을 보여준다.
   - 결제 취소 시 이전 단계로 돌아갈 수 있도록 실패 결과를 반환한다.
*/

#include <iostream> // 콘솔 입출력 (std::cout, std::cin)
#include <string>   // 문자열 처리 (std::string)
#include <limits>   // 입력 버퍼 정리 (std::numeric_limits<streamsize>::max)
#include <sstream>  // 문자열 구성 (std::ostringstream)
#include <iomanip>  // 출력 포맷 (std::setw, std::setfill)
#include <thread>   // 대기 처리 (std::this_thread::sleep_for)
#include <chrono>   // 시간 단위 (std::chrono::seconds)
#include <cstdlib>  // 시스템 명령 (system)

#include "Payment.h"     // 결제 결과/인터페이스 (ReceiptResult, ProcessPayment)
#include "ConsoleUtil.h" // 콘솔 화면 정리 (ClearScreen)

using namespace std;

namespace
{
    // 장바구니 출력
    void PrintCart(const data::json &cart)
    {
        cout << "------------------------------------------\n";
        cout << "장바구니 목록\n";
        cout << "------------------------------------------\n";

        if (!cart.contains("categories") || !cart["categories"].is_array() || cart["categories"].empty())
        {
            cout << "장바구니에 담긴 메뉴가 없습니다.\n";
            return;
        }

        for (const auto &cat : cart["categories"])
        {
            if (!cat.contains("name") || !cat.contains("items"))
                continue;
            if (!cat["items"].is_array() || cat["items"].empty())
                continue;

            cout << "\"" << cat["name"].get<string>() << "\"\n";
            for (const auto &it : cat["items"])
            {
                string name = it.value("name", "");
                int qty = it.value("qty", 0);
                int total = it.value("total", 0);
                cout << " - \"" << name << "\" : " << qty << " 개 (" << total << "원)\n";
            }
            cout << "\n";
        }
    }

    int CalcCartTotal(const data::json &cart)
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

    string GetCardBrand(const string &card4)
    {
        if (card4.size() < 2)
            return "알 수 없는 카드";
        string prefix = card4.substr(0, 2);
        if (prefix == "10")
            return "현대카드";
        if (prefix == "20")
            return "삼성카드";
        if (prefix == "30")
            return "신한카드";
        if (prefix == "40")
            return "국민카드";
        return "알 수 없는 카드";
    }

    bool Is4Digit(const string &s)
    {
        if (s.size() != 4)
            return false;
        for (char c : s)
            if (c < '0' || c > '9')
                return false;
        return true;
    }

    string BuildDateTime()
    {
        std::time_t now = std::time(nullptr);
        std::tm local_tm{};
#if defined(_WIN32)
        localtime_s(&local_tm, &now);
#else
        localtime_r(&now, &local_tm);
#endif
        std::ostringstream oss;
        oss << (local_tm.tm_year + 1900) << "-"
            << std::setw(2) << std::setfill('0') << (local_tm.tm_mon + 1) << "-"
            << std::setw(2) << std::setfill('0') << local_tm.tm_mday << " "
            << std::setw(2) << std::setfill('0') << local_tm.tm_hour << ":"
            << std::setw(2) << std::setfill('0') << local_tm.tm_min;
        return oss.str();
    }

    data::json BuildItemsArray(const data::json &cart)
    {
        data::json items = data::json::array();
        if (!cart.contains("categories") || !cart["categories"].is_array())
            return items;

        for (const auto &cat : cart["categories"])
        {
            string category = cat.value("name", "");
            if (!cat.contains("items") || !cat["items"].is_array())
                continue;
            for (const auto &it : cat["items"])
            {
                string name = it.value("name", "");
                int qty = it.value("qty", 0);
                if (qty <= 0)
                    continue;
                items.push_back({{"category", category}, {"name", name}, {"qty", qty}});
            }
        }
        return items;
    }

    void PrintReceiptAndWait(const data::json &receipt)
    {
        cout << "------------------------------------------\n";
        if (receipt.contains("count"))
            cout << "제 " << receipt["count"].get<int>() << "번째 손님 영수증\n";
        cout << "결제 시각 : " << receipt.value("datetime", "") << "\n";
        cout << "결제 방식 : " << receipt.value("method", "") << "\n";
        cout << "------------------------------------------\n";

        if (receipt.contains("items") && receipt["items"].is_array())
        {
            for (const auto &it : receipt["items"])
            {
                string category = it.value("category", "");
                string name = it.value("name", "");
                int qty = it.value("qty", 0);
                cout << "- " << category << " / " << name << " : " << qty << "개\n";
            }
        }

        cout << "------------------------------------------\n";
        cout << "최종 결제 금액 : " << receipt.value("amount", 0) << "원\n";
        cout << "------------------------------------------\n";
        cout << "10초 후 자동으로 다음 화면으로 이동합니다.\n";
#if defined(_WIN32)
        // Windows: 시스템 명령으로 10초 대기
        system("timeout /t 10 > nul");
#else
        // Linux/mac: system("sleep 10") 으로 대체 가능
        std::this_thread::sleep_for(std::chrono::seconds(10));
#endif
    }
} // namespace

namespace payment
{
    // 결제 처리: 카드/현금 분기 후 영수증 JSON 생성
    ReceiptResult ProcessPayment(const data::json &cart, int nextCount)
    {
        // 입출력을 빠르게 만들기 위한 설정
        ios::sync_with_stdio(false);
        cin.tie(nullptr);

        ClearScreen();
        cout << "------------------------------------------\n";
        cout << "결제 화면\n";
        cout << "------------------------------------------\n\n";
        PrintCart(cart);
        int total = CalcCartTotal(cart);
        cout << "총 금액 : " << total << "원\n";
        cout << "------------------------------------------\n\n";

        int method = 0;
        while (true)
        {
            cout << "결제 방식 선택\n";
            cout << "1. 카드  2. 현금\n";
            cout << "------------------------------------------\n";
            cout << "입력 : ";

            cin >> method;
            if (!cin)
            {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                continue;
            }
            if (method == 1 || method == 2)
                break;

            cout << "잘못된 결제 방식입니다. 다시 입력해주세요.\n";
        }

        string methodStr;
        int finalAmount = total;

        if (method == 1)
        {
            string card4;
            string brand;
            while (true)
            {
                cout << "\n카드번호 4자리를 입력해주세요.\n";
                cout << "입력 : ";
                cin >> card4;

                if (!Is4Digit(card4))
                {
                    cout << "4자리 숫자만 입력하세요. 다시 입력해주세요.\n";
                    continue;
                }
                brand = GetCardBrand(card4);
                if (brand == "알 수 없는 카드")
                {
                    cout << "지원하지 않는 카드번호입니다. 다시 입력해주세요.\n";
                    continue;
                }
                break;
            }

            cout << "\n"
                 << brand << "(" << card4 << ")\n";
            cout << "결제하시겠습니까? (Y/N)\n";
            cout << "입력 : ";
            string yn;
            cin >> yn;
            if (!(yn == "Y" || yn == "y"))
            {
                cout << "결제가 취소되었습니다. 이전 메뉴로 돌아갑니다.\n";
                return {false, data::json::object(), 0};
            }

            methodStr = brand + "(" + card4 + ")";
        }
        else if (method == 2)
        {
            // 현금은 10% 할인
            finalAmount = total * 90 / 100;
            methodStr = "현금";
            cout << "\n현금 결제는 10% 할인이 적용됩니다.\n";
            cout << "할인 적용 금액 : " << finalAmount << "원\n\n";

            int receivedSum = 0;
            while (true)
            {
                int remain = finalAmount - receivedSum;
                if (remain < 0)
                    remain = 0;
                cout << "현재 받은 금액 : " << receivedSum << "원\n";
                cout << "남은 결제 금액 : " << remain << "원\n";
                cout << "입금액을 입력하세요 (취소: 0)\n";
                cout << "입력 : ";

                int pay = 0;
                cin >> pay;
                if (!cin)
                {
                    cin.clear();
                    cin.ignore(numeric_limits<streamsize>::max(), '\n');
                    continue;
                }
                if (pay == 0)
                {
                    cout << "결제가 취소되었습니다. 이전 메뉴로 돌아갑니다.\n";
                    return {false, data::json::object(), 0};
                }
                if (pay < 0)
                    continue;

                receivedSum += pay;
                if (receivedSum >= finalAmount)
                {
                    int change = receivedSum - finalAmount;
                    cout << "\n거스름돈 : " << change << "원\n";
                    break;
                }
            }
        }
        else
        {
            cout << "잘못된 결제 방식입니다.\n";
            return {false, data::json::object(), 0};
        }

        data::json receipt;
        receipt["count"] = nextCount;
        receipt["datetime"] = BuildDateTime();
        receipt["items"] = BuildItemsArray(cart);
        receipt["method"] = methodStr;
        receipt["amount"] = finalAmount;

        PrintReceiptAndWait(receipt);
        return {true, receipt, finalAmount};
    }
} // namespace payment

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/
