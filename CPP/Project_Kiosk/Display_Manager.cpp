/*
   제작 시간 : 0227_21:40
   유형 : 과제
   주제 : 키오스크 만들기 - 메뉴 관리 화면
   설명 :
   - menu.json을 읽어 카테고리/메뉴 목록을 관리한다.
   - 카테고리/메뉴 추가·삭제, 메뉴 가격 변경 기능을 제공한다.
   - 수정/삭제 작업은 access_control.json의 현재 로그인 ID로 비밀번호를 재확인한다.
   - 입력은 ReadLineStrict 기준으로 처리되며, 가격은 0 초과 정수만 허용한다.
   - 카테고리 삭제는 2회 확인, 메뉴 삭제/가격 변경은 1회 확인을 거친다.
*/

#include <iostream> // 콘솔 입출력 (std::cout)
#include <string>   // 문자열 처리 (std::string)
#include <thread>   // 대기 처리 (std::this_thread::sleep_for)
#include <chrono>   // 시간 단위 (std::chrono::seconds)

#include "Display_Manager.h"
#include "DataManager.h"  // JSON 읽기/쓰기 (data::ReadJsonFile, WriteJsonFile)
#include "ConsoleUtil.h"  // 콘솔/입력 유틸 (ClearScreen, ReadLineStrict, ReadMaskedInput, TryParseIntExact, PromptYesNo, PromptPositiveInt)

using namespace std;

namespace
{
bool LoadMenuJson(data::json &root)
{
    if (!data::ReadJsonFile(data::path_MenuData, root))
    {
        root = data::json::object();
        root["categories"] = data::json::array();
        return true;
    }
    if (!root.contains("categories") || !root["categories"].is_array())
        root["categories"] = data::json::array();
    return true;
}

bool SaveMenuJson(const data::json &root)
{
    return data::WriteJsonFile(data::path_MenuData, root);
}

bool CheckPassword(const string &userId, const string &pw)
{
    data::json auth;
    if (!data::ReadJsonFile(data::path_AccessControl, auth))
        return false;
    if (!auth.contains("users") || !auth["users"].is_array())
        return false;

    for (const auto &u : auth["users"])
    {
        if (!u.contains("id") || !u.contains("pw"))
            continue;
        if (u["id"].get<string>() == userId)
            return u["pw"].get<string>() == pw;
    }
    return false;
}

bool ConfirmPassword(const string &userId)
{
    for (int attempt = 1; attempt <= 3; ++attempt)
    {
        ClearScreen();
        cout << "접속 중인 아이디: " << userId << "\n";
        cout << "비밀번호 : ";
        string pw = ReadMaskedInput(0, false);
        if (CheckPassword(userId, pw))
            return true;

        cout << "비밀번호가 틀렸습니다. 남은 횟수: " << (3 - attempt) << "\n";
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    return false;
}

bool CategoryAdd(data::json &root, const string &userId)
{
    if (!ConfirmPassword(userId))
        return false;

    ClearScreen();
    cout << "추가할 카테고리 이름을 입력하세요.\n";
    cout << "입력 : ";
    string name;
    if (!ReadLineStrict(name))
        return true;

    for (const auto &c : root["categories"])
    {
        if (c.value("name", "") == name)
        {
            cout << "이미 존재하는 카테고리입니다.\n";
            std::this_thread::sleep_for(std::chrono::seconds(1));
            return true;
        }
    }

    data::json cat;
    cat["name"] = name;
    cat["items"] = data::json::array();
    root["categories"].push_back(cat);
    SaveMenuJson(root);
    return true;
}

bool CategoryDelete(data::json &root, const string &userId)
{
    if (root["categories"].empty())
    {
        cout << "삭제할 카테고리가 없습니다.\n";
        std::this_thread::sleep_for(std::chrono::seconds(1));
        return true;
    }

    while (true)
    {
        ClearScreen();
        cout << "--------------------------------------\n";
        cout << "[카테고리 - 삭제]\n";
        cout << "--------------------------------------\n";
        for (size_t i = 0; i < root["categories"].size(); ++i)
            cout << (i + 1) << ". " << root["categories"][i].value("name", "") << "\n";
        cout << "--------------------------------------\n";
        cout << "관리자 메뉴로 돌아가려면 out을 입력하세요.\n";
        cout << "입력 : ";

        string line;
        if (!ReadLineStrict(line))
            continue;
        if (line == "out")
            return false;

        int idx = 0;
        if (!TryParseIntExact(line, idx))
            continue;
        if (idx < 1 || idx > static_cast<int>(root["categories"].size()))
            continue;

        if (!ConfirmPassword(userId))
            return false;

        if (!PromptYesNo("정말 삭제하겠습니까?", true))
            return true;
        if (!PromptYesNo("정말 정말 삭제하겠습니까?", true))
            return true;

        root["categories"].erase(root["categories"].begin() + (idx - 1));
        SaveMenuJson(root);
        return true;
    }
}

bool MenuAdd(data::json &root, size_t catIdx, const string &userId)
{
    if (!ConfirmPassword(userId))
        return false;

    ClearScreen();
    cout << "추가할 메뉴 이름을 입력하세요.\n";
    cout << "입력 : ";
    string name;
    if (!ReadLineStrict(name))
        return true;

    int price = 0;
    if (!PromptPositiveInt("가격을 입력하세요.", price, true))
        return true;

    if (!PromptYesNo("정말 추가하시겠습니까?", true))
        return true;

    data::json item;
    item["name"] = name;
    item["price"] = price;
    root["categories"][catIdx]["items"].push_back(item);
    SaveMenuJson(root);
    return true;
}

bool MenuDelete(data::json &root, size_t catIdx, const string &userId)
{
    auto &items = root["categories"][catIdx]["items"];
    if (!items.is_array() || items.empty())
    {
        cout << "삭제할 메뉴가 없습니다.\n";
        std::this_thread::sleep_for(std::chrono::seconds(1));
        return true;
    }

    while (true)
    {
        ClearScreen();
        cout << "--------------------------------------\n";
        cout << "[메뉴 - 삭제]\n";
        cout << "--------------------------------------\n";
        for (size_t i = 0; i < items.size(); ++i)
            cout << (i + 1) << ". " << items[i].value("name", "") << "\n";
        cout << "--------------------------------------\n";
        cout << "관리자 메뉴로 돌아가려면 out을 입력하세요.\n";
        cout << "입력 : ";

        string line;
        if (!ReadLineStrict(line))
            continue;
        if (line == "out")
            return false;

        int idx = 0;
        if (!TryParseIntExact(line, idx))
            continue;
        if (idx < 1 || idx > static_cast<int>(items.size()))
            continue;

        if (!ConfirmPassword(userId))
            return false;

        if (!PromptYesNo("정말 삭제하겠습니까?", true))
            return true;

        items.erase(items.begin() + (idx - 1));
        SaveMenuJson(root);
        return true;
    }
}

bool ChangePrice(data::json &root, size_t catIdx, size_t itemIdx, const string &userId)
{
    auto &item = root["categories"][catIdx]["items"][itemIdx];
    ClearScreen();
    cout << "선택 메뉴: " << item.value("name", "") << "\n";
    cout << "현재 가격: " << item.value("price", 0) << "원\n";

    int price = 0;
    if (!PromptPositiveInt("변경할 가격을 입력하세요.", price, true))
        return true;

    if (!ConfirmPassword(userId))
        return false;

    if (!PromptYesNo("가격을 변경하시겠습니까?", true))
        return true;

    item["price"] = price;
    SaveMenuJson(root);
    return true;
}

bool MenuAddDelete(data::json &root, size_t catIdx, const string &userId)
{
    while (true)
    {
        ClearScreen();
        cout << "--------------------------------------\n";
        cout << "[음식 - 추가 삭제]\n";
        cout << "--------------------------------------\n";
        cout << "1. 추가\n";
        cout << "2. 삭제\n";
        cout << "--------------------------------------\n";
        cout << "관리자 메뉴로 돌아가고 싶다면 out을 입력해주세요.\n";
        cout << "입력 : ";

        string line;
        if (!ReadLineStrict(line))
            continue;
        if (line == "out")
            return false;

        int sel = 0;
        if (!TryParseIntExact(line, sel))
            continue;
        if (sel == 1)
            return MenuAdd(root, catIdx, userId);
        if (sel == 2)
            return MenuDelete(root, catIdx, userId);
    }
}

bool CategoryAddDelete(data::json &root, const string &userId)
{
    while (true)
    {
        ClearScreen();
        cout << "--------------------------------------\n";
        cout << "[카테고리 - 추가 삭제]\n";
        cout << "--------------------------------------\n";
        cout << "1. 추가\n";
        cout << "2. 삭제\n";
        cout << "--------------------------------------\n";
        cout << "관리자 메뉴로 돌아가고 싶다면 out을 입력해주세요.\n";
        cout << "입력 : ";

        string line;
        if (!ReadLineStrict(line))
            continue;
        if (line == "out")
            return false;

        int sel = 0;
        if (!TryParseIntExact(line, sel))
            continue;
        if (sel == 1)
            return CategoryAdd(root, userId);
        if (sel == 2)
            return CategoryDelete(root, userId);
    }
}

bool ManageCategory(data::json &root, size_t catIdx, const string &userId)
{
    while (true)
    {
        ClearScreen();
        cout << "--------------------------------------\n";
        cout << "카테고리 [" << root["categories"][catIdx].value("name", "") << "] 메뉴 가격\n";
        cout << "--------------------------------------\n";

        auto &items = root["categories"][catIdx]["items"];
        if (items.is_array())
        {
            for (size_t i = 0; i < items.size(); ++i)
                cout << (i + 1) << ". " << items[i].value("name", "") << "\n";
        }

        cout << "--------------------------------------\n";
        cout << "\"메뉴\"에 대응하는 번호를 입력 시 \"가격\"으로 접속할 수 있습니다.\n";
        cout << "메뉴를 추가/삭제하려면 0을 입력해주세요.\n";
        cout << "관리자 메뉴로 돌아가고 싶다면 out을 입력해주세요.\n";
        cout << "입력 : ";

        string line;
        if (!ReadLineStrict(line))
            continue;
        if (line == "out")
            return false;
        if (line == "0")
        {
            if (!MenuAddDelete(root, catIdx, userId))
                return false;
            continue;
        }

        int idx = 0;
        if (!TryParseIntExact(line, idx))
            continue;
        if (!items.is_array() || idx < 1 || idx > static_cast<int>(items.size()))
            continue;

        if (!ChangePrice(root, catIdx, idx - 1, userId))
            return false;
    }
}
} // namespace

namespace display_manager
{
    void RunMenuManage(const std::string &userId)
    {
        data::json root;
        if (!LoadMenuJson(root))
        {
            cout << "menu.json을 읽을 수 없습니다.\n";
            std::this_thread::sleep_for(std::chrono::seconds(1));
            return;
        }

        while (true)
        {
            ClearScreen();
            cout << "--------------------------------------\n";
            cout << "[카테고리] 메뉴 가격\n";
            cout << "--------------------------------------\n";
            for (size_t i = 0; i < root["categories"].size(); ++i)
                cout << (i + 1) << ". " << root["categories"][i].value("name", "") << "\n";
            cout << "--------------------------------------\n";
            cout << "\"카테고리\"에 대응하는 번호를 입력 시 \"메뉴\"로 접속할 수 있습니다.\n";
            cout << "카테고리를 추가/삭제하려면 0을 입력해주세요.\n";
            cout << "관리자 메뉴로 돌아가고 싶다면 out을 입력해주세요.\n";
            cout << "--------------------------------------\n";
            cout << "입력 : ";

            string line;
            if (!ReadLineStrict(line))
                continue;
            if (line == "out")
            {
                ClearScreen();
                return;
            }
            if (line == "0")
            {
                if (!CategoryAddDelete(root, userId))
                    return;
                continue;
            }

            int idx = 0;
            if (!TryParseIntExact(line, idx))
                continue;
            if (idx < 1 || idx > static_cast<int>(root["categories"].size()))
                continue;

            if (!ManageCategory(root, idx - 1, userId))
                return;
        }
    }
} // namespace display_manager




