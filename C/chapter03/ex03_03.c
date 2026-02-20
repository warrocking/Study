/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 선언
    short sh = 32768;
    int in = 2147483648;
    long ln = 2147483648;
    long long lnln = 9223372036854775808;

    // 입력

    // 처리

    // 출력
    printf("short형 변수 최대값 : %d\n", sh - 1);
    printf("int형 변수 최대값 : %d\n", in - 1);
    printf("long형 변수 최대값 : %ld\n", ln - 1);
    printf("long long형 변수 최대값 : %lld\n", lnln - 1);

    printf("\n");

    printf("short형 변수 최소값 : %d\n", sh);
    printf("int형 변수 최소값 : %d\n", in);
    printf("long형 변수 최소값 : %ld\n", ln);
    printf("long long형 변수 최소값 : %lld\n", lnln);

    printf("\n");

    printf("short형 변수 unsigned값 : %u\n", sh);
    printf("int형 변수 unsigned값 : %u\n", in);
    printf("long형 변수 unsigned값 : %lu\n", ln);
    printf("long long형 변수 unsigned값 : %llu\n", lnln);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/