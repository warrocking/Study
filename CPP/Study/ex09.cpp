/*
   제작 시간 : 0227_09:42
    유형 : 예제
    주제 : 짝수 출력하기
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
    int value = 0;
    int count = 0;
    int sum = 0;
    // 데이터 준비 및 입력
    cout << "몇 수까지 짝수 판별? : ";
    cin >> value;
    count = 0;

    // 로직 처리
    for (int i = 1; i <= value; i++)
    {
        if (i % 2 == 0)
        {
            cout << "짝수 : " << i << "\n";
            count++;
            sum += i;
        }
    }
    cout << "총 짝수 개수 : " << count << "\n";
    cout << "총 짝수 합 : " << sum << "\n";
    // 결과 출력

    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/