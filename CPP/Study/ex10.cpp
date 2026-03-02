/*
   제작 시간 : 0227_10:19
    유형 : 예제
    주제 : 구구단 만들기
    문제 설명:
    -
*/

#include <iostream>
// 필요할 때만 주석 해제:
// #include <string>    // std::string 사용 시
// #include <vector>    // std::vector 사용 시
// #include <algorithm> // sort, max, min 등
// #include <cmath>     // 수학 함수

using namespace std;

// 함수 선언

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // 변수 선언 및 초기화
    int value;
    while (1)
    {
        value = 0;
        cout << "구구단 출력\n"
             << "전체 출력을 원할 시 '10'입력\n"
             << "종료를 원할 시 '0' 입력\n"
             << "원하는 단을 입력 : ";
        cin >> value;
        if (value > 0 && value < 10)
        {
            cout << "---------" << value << "단---------\n";
            for (int i = 1; i < 10; i++)
            {
                cout << "\t" << value << "*" << i << "=" << value * i << "\n";
            }
            cout << "---------------------" << "\n\n";
        }
        else if (value == 10)
        {
            for (int i = 1; i < 10; i++)
            {
                cout << "---------" << i << "단---------\n";
                for (int j = 1; j < 10; j++)
                {

                    cout << "\t" << i << "*" << j << "=" << i * j << "\n";
                }
            }
            cout << "---------------------" << "\n\n";
        }
        else if (value == 0)
        {
            cout << "---------------------"
                 << "\n\n"
                 << "프로그램 종료\n";
            break;
        }
        else
        {
            cout << "잘못된 입력. 재입력을 하시오.\n";
        }
    }
    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력

    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/