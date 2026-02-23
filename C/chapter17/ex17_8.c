/*
    제작 시간 : 0223_15:45
    유형 : 예제
    주제 : 구조체 배열을 처리하는 함수
    문제 설명: 함수에서 -> 연산자를 사용하여 구조체 배열의 값 출력
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

/* 함수 선언 공간 */
// ------- 시작 ----------
struct address
{
    char name[20];
    int age;
    char tel[20];
    char address[80];
};

void print_list(struct address *lp)
{
    for (int i = 0; i < 5; i++)
    {
        printf("%s\t%d\t%s\t%s\n",
               (lp + i)->name,
               (lp + i)->age,
               (lp + i)->tel,
               (lp + i)->address);
    }
}
// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    struct address list[5] = {
        {"홍길동", 23, "111-1111", "울릉도-독도"},
        {"이순신", 35, "222-2222", "서울 건천동"},
        {"장보고", 19, "333-3333", "완도 강해진"},
        {"유관순", 15, "444-4444", "충남 천안"},
        {"안중근", 45, "555-5555", "황해도 해주"}};

    /*        입 력       */

    /*        처 리       */
    print_list(list);

    /*        출 력       */

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
