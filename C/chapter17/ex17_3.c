/*
    제작 시간 : 0223_11:59
    유형 : 예제
    제목 : 다른 구조체를 멤버로 갖는 구조체 사용

    개념
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
struct profile
{
    int age;
    double height;
};
struct student
{
    struct profile pf;
    int id;
    double grade;
};

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    struct student yuni;

    /*        입 력       */
    yuni.pf.age = 17;
    yuni.pf.height = 164.5;
    yuni.id = 315;
    yuni.grade = 4.3;
    /*        처 리       */

    /*        출 력       */
    printf("나이 : %d\n", yuni.pf.age);
    printf("키 : %.1lf\n", yuni.pf.height);
    printf("학번 : %d\n", yuni.id);
    printf("학점 : %.1lf\n", yuni.grade);
    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
