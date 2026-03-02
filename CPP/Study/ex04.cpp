/*
   제작 시간 : 0226_15:20
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
    int value_sum = value_a + value_b;
    int value_diff = value_a > value_b ? value_a - value_b : value_b - value_a;
    int value_mul = value_a * value_b;
    int value_div = value_a > value_b ? value_a / value_b : value_b / value_a;
    int value_mod = value_a > value_b ? value_a % value_b : value_b % value_a;

    // 결과 출력
    std::cout << "합 : " << value_sum << "\n";
    std::cout << "차 : " << value_diff << "\n";
    std::cout << "곱 : " << value_mul << "\n";
    std::cout << "몫 : " << value_div << "\n";
    std::cout << "나머지 : " << value_mod << "\n";
    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/