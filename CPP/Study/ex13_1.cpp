/*
   제작 시간 : 0227_12:30
    유형 : 예제
    주제 : 복합 타입의 모든것
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
    int target = 20;
    int &ref = target;
    cout << "ref : " << ref << "\n";
    cout << "target = " << target << "\n";
    cout << "&ref = " << &ref << "\n";
    cout << "&target = " << &target << "\n";

    ref = 100;
    cout << "ref : " << ref << "\n";
    cout << "target = " << target << "\n";
    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력

    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/