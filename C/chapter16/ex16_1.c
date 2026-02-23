/*
    문제 요약 : 동적 할당한 저장 공간을 사용하는 프로그램

    문제 설명
    - heap의 20byte int형을 만들어 사용하는 것.
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
    int sum = 0;
    int *pi;
    double *pd;

    // 데이터 준비 및 입력
    pi = (int *)malloc(sizeof(int));       // 스택
    pi = (int *)malloc(20);                // heap
    pd = (double *)malloc(sizeof(double)); // 공간

    // 로직 처리
    if (pi == NULL)
    {
        printf("# 메모리가 부족합니다.\n");
        exit(1);
    }
    // heap에 확보한 정수공간에 나이를 입력받고 총 나이 합과 평균을 구해보기.
    printf("다섯 명의 나이를 입력하시오 : ");
    for (int i = 0; i < 5; i++)
    {
        scanf("%d", &pi[i]);
        // scanf("%d", &pi + i);
        // sum += pi[i];
    }
    *pi = 10;
    *pd = 3.4;

    // 결과 출력
    printf("&a : %p\n", &a);
    printf("a : %d\n", a);
    printf("pi : %p\n", pi);
    printf("*pi : %d\n", *pi);

    printf("총 나이의 합 = %d\n", sum);
    printf("평균 나이 : %.1lf\n", sum / 5.0);

    // 함수종료
    free(pi);
    free(pd);
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/