/*
    제작 시간 : 0225_19:53
    유형 : 연습
    주제 : p538 2
    문제 설명:
    - 연결 리스트를 만들수 있도록 코드 제작
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
typedef struct train Train;

struct train
{
    int seats;
    struct train *next;
};

// 전역 변수

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    Train *head = NULL, *tail = NULL;
    /*        입 력       */

    /*        처 리       */
    for (int i = 0; i < 5; i++)
    {
        if (head == NULL)
        {
            head = tail = (Train *)malloc(sizeof(Train));
        }
        else
        {
            tail->next = (Train *)malloc(sizeof(Train));
            tail = tail->next;
        }
    }
    /*        출 력       */

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
