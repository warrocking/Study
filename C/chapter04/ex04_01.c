/*
    문제 요약 : 대입, 더하기, 뺴기, 곱하기, 음수 연산

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
    int a, b;
    int sum, mul, sub, inv;
    double div;

    // 데이터 준비 및 입력
    a = 10;
    b = 20;

    // 로직 처리
    sum = a + b;
    mul = a * b;
    sub = a - b;
    div = (double)a / b;

    inv = -a;

    // 결과 출력
    printf("a의 값 : %d\n", a);
    printf("b의 값 : %d\n", b);
    printf("a와 b의 합 값 : %d\n", sum);
    printf("a와 b의 곱하기 값 : %d\n", mul);
    printf("a와 b의 차 값 : %d\n", sub);
    printf("a와 b의 나누기 값 : %.1lf\n", div);
    printf("a의 역수 값 : %d\n", inv);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/