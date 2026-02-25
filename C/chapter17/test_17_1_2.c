/*
    제작 시간 : 0225_19:43
    유형 : 연습
    주제 : p519 2
    문제 설명: 크래커의 가격(price)과 열량(calories)을 저장할 cracker 구조체를 선언합니다.
    - 그리고 그 구조체로 변수를 선언하고 가격과 열량을 키보드로 입력하면 입력값을 화면에 출력하는 프로그램을 작성.
    -
    - 바사삭의 가격과 열량을 입력하시오 : 1200 500
    - 바사삭의 가격 : 1200원
    - 바사삭의 열량 : 500kcal
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
struct cracker
{
    int price;
    double calories;
};

// 전역 변수

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    struct cracker cookie;

    /*        입 력       */
    printf("바사삭의 가격과 열량을 입력하세오 : ");
    scanf("%d %.1lf", &cookie.price, &cookie.calories);

    /*        처 리       */

    /*        출 력       */
    printf("바사삭의 가격 : %d원\n", cookie.price);
    printf("바사삭의 열량 : %.1lfkcal\n", cookie.calories);

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
