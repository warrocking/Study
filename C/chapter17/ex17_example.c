/*
    제작 시간 : 0225_10:41
    유형 : 과제
    주제 :
    문제 설명:
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
    int *pi = NULL;
    int count = 0;

    printf("malloc 갯수 입력 : ");
    if (scanf("%d", &count) != 1 || count <= 0)
    {
        printf("올바른 양의 정수를 입력하세요.\n");
        return 1;
    }
    pi = (int *)malloc((size_t)count * sizeof(int));
    if (!pi)
    {
        printf("메모리 할당 실패\n");
        return 1;
    }
    /*        처 리       */
    for (int i = 0; i < count; i++)
    {
        pi[i] = i;
        printf("pi[%d] addr=%p , val=%d\n", i, &pi[i], pi[i]);
    }

    /*        출 력       */

    /* 함수 종료 */

    free(pi);

    return 0;
}

/* 함수 정의 공간 */
