/*
   제작 시간 : 0227_20:43
   유형 : 과제
   주제 : 키오스크 만들기 - 중앙 관리 프로그램
   설명 :
   - 프로그램 전체 실행 흐름을 담당한다.
   - 로그인 성공 후 관리자 메뉴를 띄우고, 메뉴 관리/매출 관리/판매 시작/종료를 선택한다.
   - 메뉴 관리는 Display_Manager, 판매는 Display_selling -> Shopping -> Payment 순서로 이어진다.
   - 결제 완료 시 영수증 JSON을 PaymentReceipt.json에 누적 저장한다.
   - Display에서 out 입력 시 판매 루프를 종료하고 관리자 메뉴로 복귀한다.
   - 매출 관리는 PaymentReceipt.json을 읽어 날짜별/월별/총 매출을 출력한다.
*/

// 일반 참조
#include <iostream> // 콘솔 입출력 (std::cout, std::cin)
#include <map>      // 매출 집계용 맵 (std::map)
#include <string>   // 문자열 처리 (std::string)
#include <vector>   // 권한 목록 (std::vector)
#include <thread>   // 카운트다운 대기 (std::this_thread::sleep_for)
#include <chrono>   // 시간 단위 (std::chrono::seconds)

// 개발자 참조 내용
#include "DataManager.h" // JSON 입출력/경로 유틸 (data::ReadJsonFile, WriteJsonFile, BuildJsonPath)
#include "Login.h"       // 관리자 로그인 흐름 (login::Login_First)
#include "Display_selling.h"  // 메뉴 출력/입력 (display::RunMenu)
#include "Display_Manager.h"  // 메뉴 관리 화면 (display_manager::RunMenuManage)
#include "Shpping.h"     // 장바구니 제한/할인 (shopping::RunShopping)
#include "Payment.h"     // 결제 처리/영수증 (payment::ProcessPayment)
#include "ConsoleUtil.h" // 콘솔 유틸 (ClearScreen, ReadLineStrict, TryParseIntExact)

using namespace std;

// 함수 선언
enum class AdminAction
{
    MenuManage = 1,
    SalesManage = 2,
    AdminManage = 3,
    SystemCheck = 4,
    SalesStart = 5,
    SystemExit = 6
};

AdminAction ShowAdmin_Menu();
bool RunSalesLoop(const string &receiptPath);
void ShowSalesReport(const string &receiptPath);
void ShowAdmin_ManageNotice();
void ShowSystemCheck();
bool HasPermission(const login::AuthInfo &auth, const std::string &perm);
bool HasAnyPermission(const login::AuthInfo &auth, const std::vector<std::string> &perms);
void ShowNoPermissionCountdown();
static std::string ExtractDate(const std::string &dateTime);
static std::string ExtractMonth(const std::string &dateTime);
static const std::string kResourcePath = "C:\\Study\\CPP\\Project_Kiosk\\Resource";
int main()
{
    // 입출력을 빠르게 만들기 위한 설정
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // 변수 선언 및 초기화
    ClearScreen(); // 최초 시작 시 화면 정리
    // 데이터 준비 및 입력

    // 로직 처리
    cout << "키오스크 시스템을 시작합니다.\n\n";

    // 1) 로그인 처리 (Login.cpp)
    login::AuthInfo auth = login::Login_First();
    if (auth.result != login::LoginResult::Success)
    {
        cout << "로그인 실패 또는 데이터 오류로 종료합니다.\n";
        return 1;
    }

    const string receiptPath = data::BuildJsonPath(kResourcePath, "PaymentReceipt.json");

    // 2) 관리자 메뉴 (판매 시작 전 단계)
    while (true)
    {
        AdminAction action = ShowAdmin_Menu();
        switch (action)
        {
        case AdminAction::MenuManage:
            if (!HasPermission(auth, "menu_manage"))
            {
                ShowNoPermissionCountdown();
                break;
            }
            display_manager::RunMenuManage(auth.id);
            break;
        case AdminAction::SalesManage:
            if (!HasAnyPermission(auth, {"sales_view", "sales_manage"}))
            {
                ShowNoPermissionCountdown();
                break;
            }
            ShowSalesReport(receiptPath);
            break;
        case AdminAction::AdminManage:
            if (!HasPermission(auth, "user_manage"))
            {
                ShowNoPermissionCountdown();
                break;
            }
            ShowAdmin_ManageNotice();
            break;
        case AdminAction::SystemCheck:
            if (!HasPermission(auth, "system_manage"))
            {
                ShowNoPermissionCountdown();
                break;
            }
            ShowSystemCheck();
            break;
        case AdminAction::SalesStart:
            if (!HasPermission(auth, "sales_start"))
            {
                ShowNoPermissionCountdown();
                break;
            }
            if (!RunSalesLoop(receiptPath))
                return 1;
            break;
        case AdminAction::SystemExit:
            if (!HasPermission(auth, "system_manage"))
            {
                ShowNoPermissionCountdown();
                break;
            }
            return 0;
        }
    }
    cout << "프로그램이 종료되었습니다.\n";

    // 결과 출력

    // 함수 정리 및 종료
    return 0;
}

AdminAction ShowAdmin_Menu() // 관리자 메뉴 표시(항목 고정)
{
    while (true)
    {
        ClearScreen();
        cout << "---------"    // \t->8개
             << "------------" // 관리자 메뉴창 이란 단어에 13개
             << "---------\n"; // 이후 8개

        cout << "\t관리자 메뉴창\t\n";

        cout << "---------"    // \t->8개
             << "------------" // 관리자 메뉴창 이란 단어에 13개
             << "---------\n"; // 이후 8개

        cout << "1. 메뉴 관리\n";
        cout << "2. 매출 확인 및 관리\n";
        cout << "3. 관리자 관리\n";
        cout << "4. 시스템 점검\n";
        cout << "5. 판매 시스템 시작\n";
        cout << "6. 시스템 종료\n";
        cout << "입력 : ";

        string line;
        if (!ReadLineStrict(line))
            continue;

        int choice = 0;
        if (!TryParseIntExact(line, choice))
            continue;
        if (choice >= 1 && choice <= 6)
            return static_cast<AdminAction>(choice);
    }
}

void ShowSalesReport(const string &receiptPath)
{
    while (true)
    {
        ClearScreen();
        cout << "-----------------------------------------\n";
        cout << "\t매출 확인 및 관리\t\n";
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

        cout << "[추가 기능 준비 중]\n";
        cout << "- 매출 초기화 / 매출 정산 / 메뉴별·카테고리별 매출\n\n";
        cout << "0을 입력하면 관리자 메뉴로 돌아갑니다.\n";
        cout << "입력 : ";

        string input;
        if (!ReadLineStrict(input))
            continue;
        if (input == "0")
            break;
    }
}

void ShowAdmin_ManageNotice()
{
    ClearScreen();
    cout << "-----------------------------------------\n";
    cout << "\t관리자 관리\t\n";
    cout << "-----------------------------------------\n\n";
    cout << "현재 기능은 준비 중입니다.\n";
    cout << "권한 순서: master > manager > staff > guest\n";
    cout << "예정 기능: 하위 계정 조회/삭제/권한 변경\n\n";
    cout << "0을 입력하면 관리자 메뉴로 돌아갑니다.\n";
    cout << "입력 : ";

    string input;
    while (true)
    {
        if (!ReadLineStrict(input))
            continue;
        if (input == "0")
            break;
        ClearScreen();
        cout << "0을 입력하면 관리자 메뉴로 돌아갑니다.\n";
        cout << "입력 : ";
    }
}

void ShowSystemCheck()
{
    ClearScreen();
    cout << "-----------------------------------------\n";
    cout << "\t시스템 점검\t\n";
    cout << "-----------------------------------------\n\n";
    cout << "권한 파일: " << data::path_AccessControl << "\n";
    cout << "메뉴 파일: " << data::path_MenuData << "\n";
    cout << "로그인 오류 파일: " << data::BuildJsonPath(kResourcePath, "LoginError.json") << "\n";
    cout << "영수증 파일: " << data::BuildJsonPath(kResourcePath, "PaymentReceipt.json") << "\n\n";
    cout << "0을 입력하면 관리자 메뉴로 돌아갑니다.\n";
    cout << "입력 : ";

    string input;
    while (true)
    {
        if (!ReadLineStrict(input))
            continue;
        if (input == "0")
            break;
        ClearScreen();
        cout << "0을 입력하면 관리자 메뉴로 돌아갑니다.\n";
        cout << "입력 : ";
    }
}

bool HasPermission(const login::AuthInfo &auth, const std::string &perm)
{
    for (const auto &p : auth.permissions)
    {
        if (p == perm)
            return true;
    }
    return false;
}

bool HasAnyPermission(const login::AuthInfo &auth, const std::vector<std::string> &perms)
{
    for (const auto &p : perms)
    {
        if (HasPermission(auth, p))
            return true;
    }
    return false;
}

void ShowNoPermissionCountdown()
{
    ClearScreen();
    cout << "권한이 없습니다. 뒤로 돌아갑니다.\n";
    for (int i = 5; i >= 1; --i)
    {
        cout << "남은 시간:\t" << i << "초";
        cout << "\r" << flush;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    cout << "\n";
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
