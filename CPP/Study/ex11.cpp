/*
   제작 시간 : 0227_10:32
    유형 : 예제
    주제 : do while 구문 만들어보기
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
    int value;
    int sum = 0;
    int count = 0;
    // 데이터 준비 및 입력
    cout << "누적합 구하기\n몇까지 더하시겠습니까? : ";
    cin >> value;

    // 로직 처리

    do
    {
        count++;
        sum += count;
        cout << count << "번째 합 : " << sum << "\n";

    } while (count < value);

    // 결과 출력

    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/