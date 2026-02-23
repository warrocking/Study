/*
    제작 시간 : 0223_14:02
    유형 : 예제
    제목 : 구조체 변수를 함수의 매개변수에 사용하기

    문제 설명
    - 구조체를 반환하여 두 변수의 값 교환
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
struct vision
{
    double left;
    double right;
};
struct vision exchange(struct vision robot) // 좌우 시력 변경
{
    double temp;

    temp = robot.left;
    robot.left = robot.right;
    robot.right = temp;

    return robot;
};
/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    struct vision robot;
    /*        입 력       */
    printf("시력 입력\n");
    printf("좌측 : ");
    scanf("%lf", &(robot.left));
    printf("우측 : ");
    scanf("%lf", &(robot.right));

    /*        처 리       */
    robot = exchange(robot);

    /*        출 력       */
    printf("바뀐 시력\n");
    printf("좌측 : %.1lf\n", robot.left);
    printf("우측 : %.1lf\n", robot.right);

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
