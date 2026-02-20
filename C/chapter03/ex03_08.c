/* 문제 요약:
   - const를 사용한 함수
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int income = 0;
    double tax;
    const double tax_rate = 0.12;

    // 데이터 준비 및 입력
    income = 456;

    // 로직 처리
    tax = income * tax_rate;

    // 결과 출력
    printf("세금은 %.1lf입니다.\n", tax);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/