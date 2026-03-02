/*
   제작 시간 : 0227_15:45
    유형 : 예제
    주제 : 기본적인 동적 메모리 할당과 해제
    문제 설명: 사용자에게 입력받은 정수의 합과 평균을 구하는 예
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

    // 데이터 준비 및 입력
    std::cout << "몇개의 FreeStore 가 필요 ";
    int input_value{0};
    std::cin >> input_value;

    // 로직 처리
    auto heap = new int[input_value]; // 여러개
    for (int i = 0; i < input_value; i++)
    {
        int value{0};
        std::cout << i + 1 << "번째 값은 ";
        cin >> value;
        heap[i] = value;
    }
    std::cout << "입력 한 값들은 \n";
    for (int i = 0; i < input_value; i++)
    {
        cout << heap[i] << "\n";
    }
    auto heap1 = new int;
    delete[] heap;
    delete heap1;

    // 결과 출력

    // 함수 정리 및 종료

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/