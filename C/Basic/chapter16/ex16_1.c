/*
    문제 요약 : 동적 할당한 저장 공간을 사용하는 프로그램

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
#include <stdlib.h>
// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int a;
    a = 100;

    int *pi;
    double *pd;

    // 데이터 준비 및 입력
    pi = (int *)malloc(sizeof(int)); // 스택
    if (pi == NULL)
    {
        printf("# 메모리가 부족합니다.\n");
        exit(1);
    }
    pd = (double *)malloc(sizeof(double)); // 공간

    *pi = 10;
    *pd = 3.4;
    // 로직 처리

    // 결과 출력
    printf("&a : %p\n", &a);
    printf("a : %d\n", a);
    printf("pi : %p\n", pi);
    printf("*pi : %d\n", *pi);

    // 함수종료
    free(pi);
    free(pd);
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/