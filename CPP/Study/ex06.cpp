/*
   제작 시간 : 0226_15:41
    유형 : 예제
    주제 : 비트연산자와 논리 연산자
    문제 설명:
    -
*/

#include <iostream>
// 필요할 때만 주석 해제:
// #include <string>    // std::string 사용 시
// #include <vector>    // std::vector 사용 시
// #include <algorithm> // sort, max, min 등
// #include <cmath>     // 수학 함수
#include <bitset>

using namespace std;

// 함수 선언

int main()
{
     ios::sync_with_stdio(false);
     cin.tie(nullptr);

     // 변수 선언 및 초기화
     unsigned char value_a = 130;
     unsigned char value_b = 65;

     unsigned short us = 0xff00;
     short s = 0xff00;
     // 데이터 준비 및 입력
     unsigned char c1, c2, c3, c4;
     c1 = value_a & value_b;
     c2 = value_a | value_b;
     c3 = value_a ^ value_b;
     c4 = ~value_a;

     unsigned short us_shift = us >> 4;
     short s_shift = s >> 4;

     // 로직 처리

     // 결과 출력
     cout << "A : " << (int)value_a << " (" << bitset<8>(value_a) << ")\n";
     cout << "B : " << (int)value_b << " (" << bitset<8>(value_b) << ")\n";
     cout << "AND(&)  : " << (int)c1 << " (" << bitset<8>(c1)
          << ")  // 둘 다 1인 비트만 남김\n";
     cout << "OR(|)   : " << (int)c2 << " (" << bitset<8>(c2)
          << ")  // 하나라도 1이면 1\n";
     cout << "XOR(^)  : " << (int)c3 << " (" << bitset<8>(c3)
          << ")  // 서로 다르면 1\n";
     cout << "NOT(~A) : " << (int)c4 << " (" << bitset<8>(c4)
          << ")  // 비트 반전\n";

     cout << "us = " << bitset<16>(us) << "(" << us << ")\n";
     cout << "us_shift = " << bitset<16>(us_shift) << "(" << us_shift << ")\n";
     cout << "s = " << bitset<16>(s) << "(" << s << ")\n";
     cout << "s_shift = " << bitset<16>(s_shift) << "(" << s_shift << ")\n";
     // 함수 정리 및 종료

     return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/
