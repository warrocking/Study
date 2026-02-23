/*
    제작 시간 : 0223_16:15
    유형 : 예제
    주제 : 자기 참조 구조체
    문제 설명: 자기 참조 구조체로 list 만들기
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
struct list
{
    int num;
    struct list *next; // 자기 자신을 가르키는 구조체   //자기 참조 구조체
};

// 전역 변수

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    struct list a = {10, NULL},
                b = {20, NULL},
                c = {30, NULL};
    struct list *head = &a, *current;

    a.next = &b;
    b.next = &c;
    c.next = 0;
    /*        입 력       */

    /*        처 리       */

    /*        출 력       */
    printf("head -> num : %d\n", head->num);
    printf("head -> next -> num : %d\n", head->next->num);
    printf("head -> next -> next -> num : %d\n", head->next->next->num);

    printf("list all : ");
    current = head;
    while (current != NULL)
    {
        printf("%d ", current->num);
        current = current->next;
    }
    printf("\n");
    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
