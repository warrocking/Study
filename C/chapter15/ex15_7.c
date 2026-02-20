/*
    문제 요약 : 함수 포인터를 사용한 함수 호출

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
int sum(int a, int b)
{
    return (a + b);
}
int minus(int a, int b)
{
    if (a > b)
        return (a - b);
    else
        return (b - a);
}
int main(void)
{
    // 변수 선언 및 초기화
    int (*fp)(int, int); // 함수 포인터 선언
    int res;

    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력
    fp = sum;
    printf("result : %d\n", fp(10, 20));

    fp = minus;
    printf("result : %d\n", fp(10, 20));

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/