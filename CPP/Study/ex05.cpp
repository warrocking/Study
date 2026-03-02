/*
   제작 시간 : 0226_15:28
    유형 : 예제
    주제 : 대소관계에 따른 bool 연산식
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
    int value_a;
    int value_b;

    // 데이터 준비 및 입력
    std::cout << "값 입력 : ";
    std::cin >> value_a;
    std::cout << "값 입력 : ";
    std::cin >> value_b;
    // 로직 처리
    bool b1 = value_a > value_b;
    bool b2 = value_a < value_b;
    bool b3 = value_a >= value_b;
    bool b4 = value_a <= value_b;
    bool b5 = value_a == value_b;
    bool b6 = value_a != value_b;
    // 결과 출력
    std::cout << std::boolalpha; // bool에서 1,0이 아니라 true, false를 출력하게 하고 싶다면 코드 추가 필수
    std::cout << "b1 : " << b1 << "\n";
    std::cout << "b2 : " << b2 << "\n";
    std::cout << "b3 : " << b3 << "\n";
    std::cout << "b4 : " << b4 << "\n";
    std::cout << "b5 : " << b5 << "\n";
    std::cout << "b6 : " << b6 << "\n";
    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/
