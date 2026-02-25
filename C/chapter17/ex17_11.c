/*
    제작 시간 : 0225_16:32
    유형 : 예제
    주제 : 구조체 활용, 공용체, 열거형
    문제 설명: 열거형을 사용한 프로그램
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
enum Season
{
    Spring = 1,
    Summer = 0,
    Fall = 5,
    Winter = 7
};
enum Keypod
{
    up = 8,
    left = 4,
    right = 6,
    douwn = 2
};
// 전역 변수
typedef unsigned int UNIT;
// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    enum season ss;
    char *pc = NULL;
    ss = Spring;
    int season = 0;
    /*        입 력       */
    printf("1 : 봄 / 2 : 여름 / 가을 : 3 / 겨울 : 4\n계절을 입력해주세요. :");
    scanf("%d", &season);

    /*        처 리       */
    switch (ss)
    {
    case Spring:
        pc = "봄";
        break;
    case Summer:
        pc = "여름";
        break;
    case Fall:
        pc = "가을";
        break;
    case Winter:
        pc = "겨울";
        break;

    default:
        break;
    }

    /*        출 력       */
    printf("나의 최애 계절은 %s입니다. \n", pc);

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
