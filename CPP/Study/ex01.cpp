/*
   제작 시간 : 0226_12:32
    유형 : 예제
    주제 : hello world 써보기
    문제 설명:
    -
*/

#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <cstring>
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
    int input_value{0};
    int a = 0;
    int b = 0;
    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력
    // :: 는 스코프 레볼루션이라는 의미
    // std는
    std::cout << "Hello World!\n";
    std::cout << "값입력 : ";
    std::cin >> input_value;
    std::cout << "입력값 : " << input_value << "\n";
    std::cout << "값 입력 후 합 출력\n"
              << "a : ";
    std::cin >> a;
    std::cout << "b : ";
    std::cin >> b;
    std::cout << "a+b : " << a + b << "\n";
    // 함수 종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/