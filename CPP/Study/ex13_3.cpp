/*
   제작 시간 : 0227_14:14
    유형 : 예제
    주제 : 레퍼런스 변수와 Const, typedef
    문제 설명:
    -
*/
struct Flags
{
    int a = 3;
    int b = 4 int : 5;
    bool c : 1
};

#include <iostream>
// 필요할 때만 주석 해제:
// #include <string>    // std::string 사용 시
// #include <vector>    // std::vector 사용 시
// #include <algorithm> // sort, max, min 등
// #include <cmath>     // 수학 함수
using UC_PTR = unsigned char *;
using UINT = unsigned int;
typedef long long LLONG;
typedef unsigned long long ULLONG;

using namespace std;

// 함수 선언

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // 변수 선언 및 초기화
    typedef unsigned char *uc_ptr;
    unsigned char ui = 'A';
    uc_ptr p = &uc;

    // 데이터 준비 및 입력
    char c = '1';
    char *pc = &c;
    char **pp = &pc;
    // if(*ppc - pc)
    //  로직 처리

    // 결과 출력

    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/