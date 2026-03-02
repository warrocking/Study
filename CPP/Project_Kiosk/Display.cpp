/*
   제작 시간 : 0227_20:48
   유형 : 과제
   주제 : 키오스크 만들기 - 화면 출력
   설명 :
   - menu.json을 읽어 카테고리/메뉴 목록을 화면에 출력한다.
   - 사용자는 번호로 메뉴 선택, </>로 카테고리 이동, 0으로 결제 단계 이동, out으로 관리자 메뉴로 복귀한다.
   - 메뉴 선택 시 수량 입력 → 최종 확인을 거쳐 장바구니(JSON)에 누적 저장한다.
   - 장바구니 화면에서는 번호를 선택해 수량을 줄이거나 삭제할 수 있다.
   - 장바구니는 카테고리/아이템 구조(JSON)로 만들어 Payment/Shopping 단계에 전달한다.
   - 화면 전환마다 콘솔을 정리해 가독성을 유지한다.
*/

#include <iostream>  // 콘솔 입출력 (std::cout, std::cin)
#include <string>    // 문자열 처리 (std::string)
#include <vector>    // 메뉴/카테고리 보관 (std::vector)
#include <algorithm> // 정렬/뒤집기 (std::reverse)

#include "Display.h"      // MenuResult 구조/인터페이스 (display::RunMenu)
#include "ConsoleUtil.h"  // 콘솔 화면 정리 (ClearScreen)

using namespace std;

// 함수 선언 (화면/메뉴 처리)
struct MenuItem
{
    string name;
    int price;
};

struct Category
{
    string name;
    vector<MenuItem> items;
};

struct CartItemRef
{
    size_t catIdx;
    size_t itemIdx;
};

// menu.json 로드
bool LoadMenuData(vector<Category> &out);
// 가격 표기(천 단위 콤마)
string FormatPrice(int value);
// 상단 카테고리 출력 (장바구니 포함 가능)
void PrintHeader(const vector<Category> &cats, size_t current, bool includeCart);
// 메뉴 목록 출력
void PrintMenu(const Category &cat);
// 하단 안내문 출력
void PrintFooter(bool inCart);
// 숫자 입력 여부 확인
bool IsNumber(const string &s);
// 장바구니에 항목 추가/누적
void AddToCart(data::json &cart, const string &category, const MenuItem &item, int qty);
// Y/N 입력 처리
bool PromptYesNo();
// 1 이상의 수량 입력 처리
int PromptPositiveInt();
// 장바구니 화면 출력(번호 포함)
vector<CartItemRef> PrintCartWithIndex(const data::json &cart);
// 장바구니 총합 계산
int CalcCartTotal(const data::json &cart);
// 입력 문자열 소문자 변환
string ToLowerCopy(string s);
// 장바구니 항목 수량 감소/삭제
void ReduceCartItem(data::json &cart, const CartItemRef &ref, string &statusMessage);
// 0~maxQty 입력 처리
int PromptRemoveQty(int maxQty);

namespace display
{
    // ProjectManager에서 호출됨.
    // - menu.json을 읽어 카테고리/메뉴를 출력
    // - 사용자 입력에 따라 장바구니(JSON)를 구성해서 반환
    //
    // menu.json 구조(배열형):
    // { "categories":[ {"name":"국","items":[{"name":"된장국","price":6000}, ...]}, ... ] }
    //
    // cart(JSON) 반환 구조:
    // { "categories":[ {"name":"국","items":[{"name":"된장국","qty":2,"total":12000}, ...]}, ... ] }
    MenuResult RunMenu()
    {
        ios::sync_with_stdio(false);
        cin.tie(nullptr);

        // 변수 선언 및 초기화 (menu.json 로드)
        vector<Category> categories;
        if (!LoadMenuData(categories) || categories.empty())
        {
            cout << "menu.json을 읽을 수 없거나 데이터가 비어 있습니다.\n";
            return {true, data::json::object()};
        }

        data::json cart;
        cart["categories"] = data::json::array();
        const size_t cartIndex = categories.size(); // 마지막 카테고리: 장바구니(동적)
        size_t currentIndex = 0;

        // 데이터 준비 및 입력

        // 로직 처리: 카테고리 이동(</>) + 메뉴 선택 + 장바구니 누적
        string statusMessage;
        while (true)
        {
            ClearScreen();
            PrintHeader(categories, currentIndex, true);
            if (!statusMessage.empty())
            {
                cout << statusMessage << "\n";
                statusMessage.clear();
            }
            vector<CartItemRef> cartIndexMap;
            if (currentIndex == cartIndex)
            {
                cartIndexMap = PrintCartWithIndex(cart);
            }
            else
            {
                PrintMenu(categories[currentIndex]);
            }
            PrintFooter(currentIndex == cartIndex);

            string input;
            cout << "입력 : ";
            cin >> input;

            string lowered = ToLowerCopy(input);
            if (lowered == "out")
            {
                ClearScreen();
                return {true, cart};
            }

            if (input == "0")
                break;

            if (input == ">")
            {
                if (currentIndex < cartIndex)
                    currentIndex++;
                continue;
            }
            if (input == "<")
            {
                if (currentIndex > 0)
                    currentIndex--;
                continue;
            }

            // 장바구니 화면: 번호 입력 시 수량 감소/삭제
            if (currentIndex == cartIndex)
            {
                if (!IsNumber(input))
                    continue;

                int sel = stoi(input);
                if (sel < 1 || sel > static_cast<int>(cartIndexMap.size()))
                    continue;

                ReduceCartItem(cart, cartIndexMap[sel - 1], statusMessage);
                continue;
            }

            if (!IsNumber(input))
                continue;

            int idx = stoi(input);
            if (idx < 1 || idx > static_cast<int>(categories[currentIndex].items.size()))
                continue;

            const MenuItem &selected = categories[currentIndex].items[idx - 1];

            ClearScreen();
            cout << "\"" << selected.name << "\" 몇 개를 추가하시겠습니까?\n";
            cout << "입력 : ";
            int qty = PromptPositiveInt();

            cout << "\"" << selected.name << "\" " << qty << "개를 장바구니에 추가할까요? (Y/N)\n";
            cout << "입력 : ";
            if (PromptYesNo())
            {
                AddToCart(cart, categories[currentIndex].name, selected, qty);
            }
        }

        // 장바구니 JSON 반환 (Payment/Shopping으로 전달용)
        return {false, cart};
    }
} // namespace display

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/

bool LoadMenuData(vector<Category> &out)
{
    data::json root;
    if (!data::ReadJsonFile(data::path_MenuData, root))
        return false;

    if (!root.contains("categories") || !root["categories"].is_array())
        return false;

    for (const auto &cat : root["categories"])
    {
        if (!cat.contains("name") || !cat.contains("items"))
            continue;
        if (!cat["items"].is_array())
            continue;

        Category c;
        c.name = cat["name"].get<string>();

        for (const auto &it : cat["items"])
        {
            if (!it.contains("name") || !it.contains("price"))
                continue;
            MenuItem m;
            m.name = it["name"].get<string>();
            m.price = it["price"].get<int>();
            c.items.push_back(m);
        }

        out.push_back(c);
    }
    return !out.empty();
}

string FormatPrice(int value)
{
    string s = to_string(value);
    string out;
    int count = 0;
    for (int i = static_cast<int>(s.size()) - 1; i >= 0; --i)
    {
        out.push_back(s[i]);
        count++;
        if (count == 3 && i != 0)
        {
            out.push_back(',');
            count = 0;
        }
    }
    reverse(out.begin(), out.end());
    return out;
}

void PrintHeader(const vector<Category> &cats, size_t current, bool includeCart)
{
    cout << "------------------------------------------\n";
    cout << "카테고리: ";
    for (size_t i = 0; i < cats.size(); ++i)
    {
        if (i == current)
            cout << "[" << cats[i].name << "] ";
        else
            cout << cats[i].name << " ";
    }
    if (includeCart)
    {
        if (current == cats.size())
            cout << "[장바구니]";
        else
            cout << "장바구니";
    }
    cout << "\n";
    cout << "------------------------------------------\n";
}

void PrintMenu(const Category &cat)
{
    for (size_t i = 0; i < cat.items.size(); ++i)
    {
        const auto &m = cat.items[i];
        cout << (i + 1) << ". " << m.name << " : " << FormatPrice(m.price) << "원\n";
    }
}

void PrintFooter(bool inCart)
{
    cout << "------------------------------------------\n"
         << "메뉴의 번호를 입력하면 해당 메뉴를 장바구니에 추가합니다. "
         << "만약 메뉴 카테고리를 바꾸고 싶다면 >, <를 입력하여 주십시오. "
         << "원하는 모든 메뉴를 장바구니에 담았다면, 0을 눌러 결제창으로 넘어갑니다. "
         << "프로그램 종료는 out을 입력하세요.\n"
         << "------------------------------------------\n";
    if (inCart)
    {
        cout << "장바구니 화면에서는 번호를 입력하면 해당 메뉴를 취소할 수 있습니다.\n"
             << "번호 선택 후 Y/N 확인, 수량 입력으로 취소 수량을 정합니다.\n"
             << "------------------------------------------\n";
    }
}

bool IsNumber(const string &s)
{
    if (s.empty())
        return false;
    for (char c : s)
    {
        if (c < '0' || c > '9')
            return false;
    }
    return true;
}

void AddToCart(data::json &cart, const string &category, const MenuItem &item, int qty)
{
    if (!cart.contains("categories") || !cart["categories"].is_array())
        cart["categories"] = data::json::array();

    // 카테고리 찾기
    for (auto &c : cart["categories"])
    {
        if (c.contains("name") && c["name"].get<string>() == category)
        {
            if (!c.contains("items") || !c["items"].is_array())
                c["items"] = data::json::array();

            for (auto &it : c["items"])
            {
                if (it.contains("name") && it["name"].get<string>() == item.name)
                {
                    int curQty = it.value("qty", 0);
                    int curTotal = it.value("total", 0);
                    it["qty"] = curQty + qty;
                    it["total"] = curTotal + item.price * qty;
                    return;
                }
            }

            c["items"].push_back({{"name", item.name}, {"qty", qty}, {"total", item.price * qty}});
            return;
        }
    }

    data::json newCat;
    newCat["name"] = category;
    newCat["items"] = data::json::array();
    newCat["items"].push_back({{"name", item.name}, {"qty", qty}, {"total", item.price * qty}});
    cart["categories"].push_back(newCat);
}

bool PromptYesNo()
{
    while (true)
    {
        string s;
        cin >> s;
        if (s == "Y" || s == "y")
            return true;
        if (s == "N" || s == "n")
            return false;

        cout << "Y 또는 N만 입력하세요.\n";
        cout << "입력 : ";
    }
}

int PromptPositiveInt()
{
    while (true)
    {
        string s;
        cin >> s;
        if (IsNumber(s))
        {
            int v = stoi(s);
            if (v > 0)
                return v;
        }

        cout << "1 이상의 숫자만 입력하세요.\n";
        cout << "입력 : ";
    }
}

vector<CartItemRef> PrintCartWithIndex(const data::json &cart)
{
    vector<CartItemRef> indexMap;
    if (!cart.contains("categories") || !cart["categories"].is_array() || cart["categories"].empty())
    {
        cout << "장바구니에 담긴 메뉴가 없습니다.\n";
        return indexMap;
    }

    int num = 1;
    for (size_t ci = 0; ci < cart["categories"].size(); ++ci)
    {
        const auto &cat = cart["categories"][ci];
        if (!cat.contains("name") || !cat.contains("items"))
            continue;
        if (!cat["items"].is_array() || cat["items"].empty())
            continue;

        cout << "\"" << cat["name"].get<string>() << "\"\n";
        for (size_t ii = 0; ii < cat["items"].size(); ++ii)
        {
            const auto &it = cat["items"][ii];
            string name = it.value("name", "");
            int qty = it.value("qty", 0);
            int total = it.value("total", 0);
            cout << num << ". \"" << name << "\" : " << qty << " 개 (\"" << FormatPrice(total) << "원\")\n";
            indexMap.push_back({ci, ii});
            num++;
        }
        cout << "\n";
    }

    int grandTotal = CalcCartTotal(cart);
    cout << "총 가격 : \"" << FormatPrice(grandTotal) << "원\"\n";
    return indexMap;
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

string ToLowerCopy(string s)
{
    for (char &c : s)
    {
        if (c >= 'A' && c <= 'Z')
            c = static_cast<char>(c - 'A' + 'a');
    }
    return s;
}

int PromptRemoveQty(int maxQty)
{
    while (true)
    {
        string s;
        cin >> s;
        if (IsNumber(s))
        {
            int v = stoi(s);
            if (v >= 0 && v <= maxQty)
                return v;
        }

        cout << "0부터 " << maxQty << "까지의 숫자만 입력하세요.\n";
        cout << "입력 : ";
    }
}

void ReduceCartItem(data::json &cart, const CartItemRef &ref, string &statusMessage)
{
    if (!cart.contains("categories") || !cart["categories"].is_array())
        return;
    if (ref.catIdx >= cart["categories"].size())
        return;

    auto &cat = cart["categories"][ref.catIdx];
    if (!cat.contains("items") || !cat["items"].is_array())
        return;
    if (ref.itemIdx >= cat["items"].size())
        return;

    auto &item = cat["items"][ref.itemIdx];
    int qty = item.value("qty", 0);
    if (qty <= 0)
        return;

    ClearScreen();
    cout << "선택한 메뉴: \"" << item.value("name", "") << "\" (" << qty << "개)\n";
    cout << "몇 개를 취소하시겠습니까? (0~" << qty << ")\n";
    cout << "입력 : ";
    int removeQty = PromptRemoveQty(qty);
    if (removeQty == 0)
    {
        statusMessage = "취소가 취소되었습니다. 장바구니로 돌아갑니다.";
        return;
    }

    cout << removeQty << "개를 취소하시겠습니까? (Y/N)\n";
    cout << "입력 : ";
    if (!PromptYesNo())
    {
        statusMessage = "취소가 취소되었습니다. 장바구니로 돌아갑니다.";
        return;
    }

    int total = item.value("total", 0);
    int newQty = qty - removeQty;
    if (newQty <= 0)
    {
        cat["items"].erase(cat["items"].begin() + static_cast<long long>(ref.itemIdx));
    }
    else
    {
        int newTotal = 0;
        if (qty > 0)
            newTotal = total * newQty / qty;
        item["qty"] = newQty;
        item["total"] = newTotal;
    }

    // 카테고리에 남은 아이템이 없으면 카테고리 제거
    if (cat["items"].empty())
    {
        cart["categories"].erase(cart["categories"].begin() + static_cast<long long>(ref.catIdx));
    }

    ClearScreen();
    statusMessage = "취소가 완료되었습니다. 장바구니로 돌아갑니다.";
}
