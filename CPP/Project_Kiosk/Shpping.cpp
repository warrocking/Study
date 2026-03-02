/*
   제작 시간 : 0227_20:45
   유형 : 과제
   주제 : 키오스크 만들기 - 장바구니 제한/할인
   설명 :
   - Display에서 만든 장바구니(JSON)에 제한 규칙을 적용한다.
   - 밥: 종류 2개 초과 또는 총 수량 3개 이상이면 실패 처리.
   - 국: 종류 3개 초과 또는 총 수량 4개 이상이면 실패 처리.
   - 반찬: menu.json의 모든 반찬을 1개 이상 선택하면 20% 할인 적용.
   - 조건 위반 시 false를 반환하여 상위 로직에서 종료 처리한다.
*/

#include <iostream> // 콘솔 출력 (std::cout)
#include <string>   // 문자열 처리 (std::string)
#include <vector>   // 반찬 목록/검사 (std::vector)

#include "Shpping.h" // 장바구니 제한/할인 인터페이스 (shopping::RunShopping)

using namespace std;

// 함수 선언

namespace shopping
{
    // 장바구니(JSON)를 받아 결제 로직으로 넘기는 자리
    bool RunShopping(data::json &cart)
    {
        // 입출력을 빠르게 만들기 위한 설정
        ios::sync_with_stdio(false);
        cin.tie(nullptr);

        // 변수 선언 및 초기화
        data::json menu;
        if (!data::ReadJsonFile(data::path_MenuData, menu))
        {
            cout << "menu.json을 읽을 수 없습니다.\n";
            return false;
        }

        // 데이터 준비 및 입력
        // cart에서 특정 카테고리 찾기
        auto findCategory = [&](const string &name) -> data::json *
        {
            if (!cart.contains("categories") || !cart["categories"].is_array())
                return nullptr;
            for (auto &c : cart["categories"])
            {
                if (c.contains("name") && c["name"].get<string>() == name)
                    return &c;
            }
            return nullptr;
        };

        // 로직 처리
        // 1) 밥 제한: 종류 2개까지만 + 총 수량 2개까지만
        if (data::json *rice = findCategory("밥"))
        {
            int typeCount = 0;
            int qtySum = 0;
            if (rice->contains("items") && (*rice)["items"].is_array())
            {
                for (const auto &it : (*rice)["items"])
                {
                    int qty = it.value("qty", 0);
                    if (qty > 0)
                    {
                        typeCount++;
                        qtySum += qty;
                    }
                }
            }

            if (typeCount > 2 || qtySum >= 3)
            {
                cout << "배터져요\n";
                return false;
            }
        }

        // 2) 국 제한: 종류 3개까지만 + 총 수량 3개까지만
        if (data::json *soup = findCategory("국"))
        {
            int typeCount = 0;
            int qtySum = 0;
            if (soup->contains("items") && (*soup)["items"].is_array())
            {
                for (const auto &it : (*soup)["items"])
                {
                    int qty = it.value("qty", 0);
                    if (qty > 0)
                    {
                        typeCount++;
                        qtySum += qty;
                    }
                }
            }

            if (typeCount > 3 || qtySum >= 4)
            {
                cout << "국은 최대 3종류/총 3개까지만 선택 가능합니다.\n";
                return false;
            }
        }

        // 3) 반찬 전부 선택 시 20% 할인
        // menu.json의 '반찬' 전체 목록 확인
        vector<string> sideAll;
        if (menu.contains("categories") && menu["categories"].is_array())
        {
            for (const auto &cat : menu["categories"])
            {
                if (cat.value("name", "") == "반찬" && cat.contains("items") && cat["items"].is_array())
                {
                    for (const auto &it : cat["items"])
                    {
                        if (it.contains("name"))
                            sideAll.push_back(it["name"].get<string>());
                    }
                }
            }
        }

        if (!sideAll.empty())
        {
            data::json *side = findCategory("반찬");
            if (side && side->contains("items") && (*side)["items"].is_array())
            {
                bool allSelected = true;
                for (const auto &name : sideAll)
                {
                    bool found = false;
                    for (const auto &it : (*side)["items"])
                    {
                        if (it.value("name", "") == name && it.value("qty", 0) > 0)
                        {
                            found = true;
                            break;
                        }
                    }
                    if (!found)
                    {
                        allSelected = false;
                        break;
                    }
                }

                if (allSelected)
                {
                    cout << "★추가 할인 적용 대상★\n모든 반찬을 선택하셔서 20% 할인이 적용됬습니다!\n";
                    for (auto &it : (*side)["items"])
                    {
                        int total = it.value("total", 0);
                        it["total"] = total * 80 / 100;
                    }
                }
            }
        }

        // 결과 출력

        // 함수 정리 및 종료
        return true;
    }
} // namespace shopping

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/
