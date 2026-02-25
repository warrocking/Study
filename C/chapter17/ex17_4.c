/*
    제작 시간 : 0223_12:22
    유형 : 예제
    제목 : 최고 학점의 학생 데이터 출력

    문제 설명
    -
*/

#ifdef _MSC_VER
#define _CRT_SECURE_NO_WARNINGS
#endif

// 기본 헤더 파일
#include <stdio.h>  // 입출력            // printf("%d\n", x); scanf("%d", &x);
#include <string.h> // 문자열            // strlen, strcmp, strcpy, strncpy, strcat, strncat, memset // 예: strcpy(dst, src);
#include <stdlib.h> // 메모리/변환/유틸   // malloc, calloc, free, atoi, strtol, qsort, bsearch, rand, srand // 예: int* p = malloc(sizeof(int) * n);

// 추가 헤더 파일 (필요 시 주석 제거 후 사용)
// #include <math.h>     // 수학             // sqrt, pow, fabs, floor, ceil // 예: double r = sqrt(x);
// #include <ctype.h>    // 문자 판별/변환    // isdigit, isalpha, isspace, tolower, toupper // 예: if (isdigit(c)) ...
// #include <stdbool.h>  // bool 타입(C99+)  // bool ok = true;
// #include <time.h>     // 시간/난수 시드   // time, clock // 예: srand((unsigned)time(NULL));

/* 함수 선언 공간 */
struct student
{
    int id;
    char name[40];
    double grade;
};

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    struct student s1 = {315, "홍길동", 2.4},
                   s2 = {316, "이순신", 3.7},
                   s3 = {317, "세종대왕", 4.4};
    struct student max; // 최초 정보 저장 및 최고 점수 정보 저장공간
    /*        입 력       */
    max = s1;
    /*        처 리       */
    if (s2.grade > max.grade)
        max = s2;
    if (s3.grade > max.grade)
        max = s3;
    /*        출 력       */
    printf("학번 : %d\n", max.id);
    printf("이름 : %s\n", max.name);
    printf("학점 : %.1lf\n", max.grade);
    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
