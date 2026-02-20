/*
    문제 요약 : 형 변환 연산자가 필요한 경우

    문제 설명
    -
    -
    -
    -
    -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int a = 20;
    int b = 3;
    double res;

    // 데이터 준비 및 입력

    // 로직 처리
    res = ((double)a) / ((double)b);
    printf("a = %d, b = %d\n", a, b);
    printf("a/b = %.1lf\n", res);

    a = (int)res;
    printf("(int)%.1lf의 결과 : %d\n", res, a);

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/