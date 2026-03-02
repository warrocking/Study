/*
   제작 시간 : 0227_12:33
    유형 : 예제
    주제 : 레퍼런스(References)를 이용해서 스왑 함수 만들기
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
void swap(int &first, int &secend) // call by reference
{

    int temp = first;
    first = secend;
    secend = temp;
}
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // 변수 선언 및 초기화
    int value_1; // 1000이면 가독성을 위해 '를 써서, 1'000 도 가능함.
    int value_2;
    cout << "첫 번쨰 값 : ";
    cin >> value_1;
    cout << "두 번쨰 값 : ";
    cin >> value_2;
    swap(value_1, value_2);

    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력
    cout << "첫 번쨰 값 : " << value_1 << "\n";
    cout << "두 번쨰 값 : " << value_2 << "\n";
    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/