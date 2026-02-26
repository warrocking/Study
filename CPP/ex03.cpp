/*
   제작 시간 : 0226_15:07
    유형 : 예제
    주제 :
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
    // 변수 선언 및 초기화
    bool is_value;
    int a;
    std::cout << "값 입력 : ";
    std::cin >> a;
    is_value = (a > 10 ? true : false);
    std::cout << is_value << "\n";

    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력
    int value_d = 10;

    double value_e = 30.5;

    value_d = static_cast<int>(value_e);
    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/