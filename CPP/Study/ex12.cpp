/*
   제작 시간 : 0227_10:50
    유형 : 예제
    주제 : 배열
    문제 설명:
    -
*/

#include <iostream>
// 필요할 때만 주석 해제:
// #include <string>    // std::string 사용 시
#include <vector> // std::vector 사용 시
// #include <algorithm> // sort, max, min 등
// #include <cmath>     // 수학 함수

using namespace std;

// 함수 선언

int main()
{

    // 변수 선언 및 초기화

    // 데이터 준비 및 입력

    std::vector<int> vec1 = {100, 88, 90, 70, 10};
    cout << "vec1.size() : " << vec1.size() << "\n";
    vec1.push_back(90);
    cout << "vec1.size() : " << vec1.size() << "\n";
    vec1.push_back(100);
    cout << "vec1.size() : " << vec1.size() << "\n";
    vec1.push_back(10);
    cout << "vec1.size() : " << vec1.size() << "\n";
    vec1.push_back(100);
    // 로직 처리
    for (auto &&score : vec1)
    {
        cout << score << "\n";
    }
    for (int i = 0; i < vec1.size(); i++) // for(sonst int & i :vec1)
    {
        // cout << "vec1.size() : " << vec1.size() << "\n";

        cout << "vec1[" << i << "] = " << vec1[i] << "\n";
    }
    // 결과 출력

    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/