/*
   제작 시간 : 0226_17:02
    유형 : 예제
    주제 : goto 함수 / while문
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
    goto ILOVEYOU;
    cout << "출력되지 않아야 하는 문자열";
// 데이터 준비 및 입력
ILOVEYOU:
    cout << "I LOVE YOU\n";

    cout << "\n\n\n";
    int count;
    int sum = 0;
    int i = 1;
    cout << "몇까지의 합 : ";
    cin >> count;

    while (i <= count)
    {
        sum += i;
        i++;
    }
    cout << "현재 i의 값 : " << i << "\n";
    cout << "현재 sum의 값 : " << sum << "\n";

    i = 1;
    sum = 0;
    while (true)
    {
        sum += i;
        i++;
        if (i > count)
            break;
    }
    cout << "현재 i의 값 : " << i << "\n";
    cout << "현재 sum의 값 : " << sum << "\n";
    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/