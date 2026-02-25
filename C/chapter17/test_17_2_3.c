/*
    제작 시간 : 0225_20:00
    유형 : 연습
    주제 : p539 3
    문제 설명:
    - 코드 실행해보기
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
typedef enum
{
    CYAN,
    MAGENTA,
    YELLOW = 5,
    BLACK
} COLOR;
typedef enum
{
    UP,
    DOWN,
    LEFT,
    RIGHT
} ARROW;

// 전역 변수

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    COLOR my_color = YELLOW, c;
    ARROW direction = UP;

    /*        입 력       */

    /*        처 리       */
    for (c = CYAN; c <= BLACK; c++)
    {
        direction++;
        direction = direction % 4;
        if (c == my_color)
            break;
    }

    /*        출 력       */
    switch (direction)
    {
    case UP:
        printf("현재 방향 : 위");
        break;
    case DOWN:
        printf("현재 방향 : 아래");
        break;
    case LEFT:
        printf("현재 방향 : 왼쪽");
        break;
    case RIGHT:
        printf("현재 방향 : 오른쪽");
        break;
    }
    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
