/*
    제작 시간 : 0223_17:00
    유형 : 연습
    주제 : p179 3번
    문제 설명: 옷 사이즈를 결정할 때, 나이가 25이고, 가슴둘레가 95인 사람의 사이즈를 출력하는 프로그램을 if문을 사용해 작성하시오.
    -
*/

#ifdef _MSC_VER
#define _CRT_SECURE_NO_WARNINGS
#endif

// 기본 헤더 파일
#include <stdio.h>  // 입출력               // printf("%d\n", x); scanf("%d", &x);
#include <string.h> // 문자열               // strlen, strcmp, strcpy, strncpy, strcat, strncat, memset // 예: strcpy(dst, src);
#include <stdlib.h> // 메모리/변환/유틸      // malloc, calloc, free, atoi, strtol, qsort, bsearch, rand, srand // 예: int* p = malloc(sizeof(int) * n);

// 추가 헤더 파일 (필요 시 주석 제거 후 사용)
// #include <math.h>      // 수학              // sqrt, pow, fabs, floor, ceil // 예: double r = sqrt(x);
// #include <ctype.h>     // 문자 판별/변환     // isdigit, isalpha, isspace, tolower, toupper // 예: if (isdigit(c)) ...
// #include <stdbool.h>   // bool 타입(C99+)    // bool ok = true;
// #include <time.h>      // 시간/난수 시드      // time, clock // 예: srand((unsigned)time(NULL));

/* ----- 선언 공간 ----- */
// 매크로 상수

// 구조 선언 (typedef / struct / enum / union ...)

// 전역 변수

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    int age = 25, chest = 95;
    char size;

    /*        입 력       */
    if (age < 20)
    {
        if (chest < 85)
            size = 's';
        else if (chest >= 85 && chest < 95)
            size = 'm';
        else
            size = 'l';
    }
    else
    {
        if (chest < 90)
            size = 's';
        else if (chest >= 85 && chest < 95)
            size = 'm';
        else
            size = 'l';
    }

    /*        처 리       */

    /*        출 력       */
    printf("사이즈는 %c입니다.\n", size);
    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
