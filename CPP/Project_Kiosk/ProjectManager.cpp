/*
   제작 시간 : 0227_20:43
   유형 : 과제
   주제 : 키오스크 만들기 - 중앙 관리 프로그램
   설명 :
   - 프로그램 전체 실행 흐름을 담당한다.
   - 로그인 성공 후 관리자 메뉴를 띄우고, 메뉴 관리/매출 관리/판매 시작/종료를 선택한다.
   - 판매 시작을 선택하면 Display -> Shopping -> Payment 순서로 이어지는 판매 루프를 실행한다.
   - 결제 완료 시 영수증 JSON을 PaymentReceipt.json에 누적 저장한다.
   - Display에서 out 입력 시 판매 루프를 종료하고 관리자 메뉴로 복귀한다.
   - 매출 관리는 PaymentReceipt.json을 읽어 날짜별/월별/총 매출을 출력한다.
*/

#include <iostream>      // 콘솔 입출력 (std::cout, std::cin)
#include <limits>        // 입력 버퍼 정리 (std::numeric_limits<streamsize>::max)
#include <map>           // 매출 집계용 맵 (std::map)
#include <string>        // 문자열 처리 (std::string)
#include <thread>        // 카운트다운 대기 (std::this_thread::sleep_for)
#include <chrono>        // 시간 단위 (std::chrono::seconds)
#include "DataManager.h" // JSON 입출력/경로 유틸 (data::ReadJsonFile, WriteJsonFile, BuildJsonPath)
#include "Login.h"       // 관리자 로그인 흐름 (login::Login_First)
#include "Display.h"     // 메뉴 출력/입력 (display::RunMenu)
#include "Shpping.h"     // 장바구니 제한/할인 (shopping::RunShopping)
#include "Payment.h"     // 결제 처리/영수증 (payment::ProcessPayment)
#include "ConsoleUtil.h" // 콘솔 화면 정리 (ClearScreen)

using namespace std;

// 함수 선언
int ShowAdminMenu();
bool RunSalesLoop(const string &receiptPath);
void ShowMenuManageNotice();
void ShowSalesReport(const string &receiptPath);
static std::string ExtractDate(const std::string &dateTime);
static std::string ExtractMonth(const std::string &dateTime);

int main()
{
    // 입출력을 빠르게 만들기 위한 설정
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // 변수 선언 및 초기화

    // 데이터 준비 및 입력

    // 로직 처리
    cout << "키오스크 시스템을 시작합니다.\n\n";

    // 1) 로그인 처리 (Login.cpp)
    login::LoginResult loginResult = login::Login_First();
    if (loginResult != login::LoginResult::Success)
    {
        cout << "로그인 실패 또는 데이터 오류로 종료합니다.\n";
        return 1;
    }

    const string receiptPath = data::BuildJsonPath("C:\\Study\\CPP\\Project_Kiosk\\Resource", "PaymentReceipt.json");

    // 2) 관리자 메뉴 (판매 시작 전 단계)
    while (true)
    {
        int choice = ShowAdminMenu();
        switch (choice)
        {
        case 1:
            ShowMenuManageNotice();
            break;
        case 2:
            ShowSalesReport(receiptPath);
            break;
        case 3:
            if (!RunSalesLoop(receiptPath))
                return 1;
            break;
        case 4:
            return 0;
        default:
            break;
        }
    }
    cout << "프로그램이 종료되었습니다.\n";

    // 결과 출력

    // 함수 정리 및 종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/

int ShowAdminMenu()
{
    while (true)
    {
        ClearScreen();
        cout << "-----------------------------------------\n";
        cout << "              관리자 메뉴창\n";
        cout << "-----------------------------------------\n";
        cout << "1. 메뉴 관리\n";
        cout << "2. 매출 관리\n";
        cout << "3. 판매 시스템 시작\n";
        cout << "4. 시스템 종료\n";
        cout << "입력 : ";

        int choice = 0;
        cin >> choice;
        if (!cin)
        {
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            continue;
        }

        if (choice >= 1 && choice <= 4)
            return choice;
    }
}

void ShowMenuManageNotice()
{
    ClearScreen();
    cout << "현재 메뉴의 직접적인 관리는 Json의 데이터 수정을 직접적으로 해주세요.\n";
    cout << "경로는 " << data::path_MenuData << " 입니다.\n\n";

    for (int i = 10; i >= 1; --i)
    {
        cout << "남은 시간:\t" << i << "초";
        cout << "\r" << flush;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    cout << "\n";
}

void ShowSalesReport(const string &receiptPath)
{
    while (true)
    {
        ClearScreen();
        cout << "-----------------------------------------\n";
        cout << "                매출 관리\n";
        cout << "-----------------------------------------\n\n";

        data::json root;
        std::map<std::string, int> dailyTotal;
        std::map<std::string, int> monthlyTotal;
        int grandTotal = 0;

        if (data::ReadJsonFile(receiptPath, root) && root.contains("receipts") && root["receipts"].is_array())
        {
            for (const auto &rec : root["receipts"])
            {
                int amount = rec.value("amount", 0);
                std::string dt = rec.value("datetime", "");
                std::string day = ExtractDate(dt);
                std::string month = ExtractMonth(dt);
                if (!day.empty())
                    dailyTotal[day] += amount;
                if (!month.empty())
                    monthlyTotal[month] += amount;
                grandTotal += amount;
            }
        }

        if (dailyTotal.empty())
        {
            cout << "결제 내역이 없습니다.\n\n";
        }
        else
        {
            cout << "[날짜별 매출]\n";
            for (const auto &p : dailyTotal)
                cout << p.first << " 총 매출 : " << p.second << "원\n";
            cout << "\n";

            cout << "[월별 매출]\n";
            for (const auto &p : monthlyTotal)
                cout << p.first << " 총 매출 : " << p.second << "원\n";
            cout << "\n";

            cout << "최종 총 매출 : " << grandTotal << "원\n\n";
        }

        cout << "0을 입력하면 관리자 메뉴로 돌아갑니다.\n";
        cout << "입력 : ";

        string input;
        cin >> input;
        if (input == "0")
            break;
    }
}

bool RunSalesLoop(const string &receiptPath)
{
    // Display -> Shopping -> Payment
    while (true)
    {
        display::MenuResult result = display::RunMenu();
        if (result.exitRequested)
        {
            ClearScreen();
            break;
        }

        // 제한/할인 조건 처리 (Shopping.cpp)
        if (!shopping::RunShopping(result.cart))
        {
            cout << "제한 조건에 의해 프로그램을 종료합니다.\n";
            return false;
        }

        // 결제 로직 (Payment.cpp)
        data::json root;
        if (!data::ReadJsonFile(receiptPath, root) || !root.contains("receipts") || !root["receipts"].is_array())
        {
            root = data::json::object();
            root["count"] = 0;
            root["receipts"] = data::json::array();
        }

        int nextCount = root.value("count", 0) + 1;
        payment::ReceiptResult receiptResult = payment::ProcessPayment(result.cart, nextCount);
        if (!receiptResult.success)
        {
            cout << "결제가 취소되었거나 실패했습니다.\n";
            continue;
        }

        root["count"] = nextCount;
        root["receipts"].push_back(receiptResult.receipt);
        data::WriteJsonFile(receiptPath, root);
    }

    return true;
}

static std::string ExtractDate(const std::string &dateTime)
{
    if (dateTime.size() >= 10)
        return dateTime.substr(0, 10); // YYYY-MM-DD
    return "";
}

static std::string ExtractMonth(const std::string &dateTime)
{
    if (dateTime.size() >= 7)
        return dateTime.substr(0, 7); // YYYY-MM
    return "";
}
