/*
   제작 시간 : 0227_11:55
    유형 : 예제
    주제 : 배열과 구조체와 포인터
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
    long IArray[20];
    long (*p)[20] = &IArray;                     // 포인터가 이 배열을 가리키게 만들고
    (*p)[3] = 300;                               // 포인터를 통해서 배열을 사용하자.
    cout << "IArray[3] : " << IArray[3] << "\n"; // 결과 확인

    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력

    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/