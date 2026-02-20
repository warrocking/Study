/*
    문제 요약 : 몫과 나머지를 구하는 연산

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
    double apple;
    int banana;
    int orange;

    // 데이터 준비 및 입력
    apple = 5.0 / 2.0;
    banana = 5 / 2;
    orange = 5 % 2;

    // 로직 처리

    // 결과 출력
    printf("apple : %.1lf\n", apple);
    printf("banana : %d\n", banana);
    printf("orange : %d\n", orange);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/