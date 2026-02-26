/*
   제작 시간 : 0226_16:21
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
    int age;
    // 데이터 준비 및 입력
    std::cout << "성인 판별\n나이 입력 : ";
    std::cin >> age;
    // 로직 처리

    // 결과 출력
    if (age <= 19)
        std::cout << "미성년자입니다.\n";
    else
        std::cout << "성인입니다.\n";
    // 함수 정리 및 종료

    cout << "\n\n\n";

    int score;
    std::cout << "성적 입력 : ";
    std::cin >> score;
    switch (score)
    {
    case 1:
    case 2:
    case 3:
        cout << "열심히 하세요\n";
        break;
    case 4:
        cout << "좀 더 노력하세요.\n";
        break;
    default:
        cout << "올바르지 않은 점수입니다.\n";
        break;
    }

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/