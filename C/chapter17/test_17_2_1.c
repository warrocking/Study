/*
    제작 시간 : 0225_19:49
    유형 : 연습
    주제 : p537 1
    문제 설명:
    - 구조체 변수와 구조체 포인터를 선언했을 떄, mp를 사용해 m1에 저장된 값을 출력하시오.
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
typedef struct marriage
{
    char name[80]; // 이름을 저장할 멤버
    int age;       // 나이를 저장할 멤버
    char gender;   // 성별을 저장할 멤버 , 남성은 m , 여성은 f 저장
    double height; // 키를 저장할 멤버
} marriage;

// 전역 변수

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    marriage m1 = {"Andy", 22, 'm', 187.5};
    marriage *mp = &m1;

    /*        입 력       */

    /*        처 리       */

    /*        출 력       */
    printf("이름 : %s\n", mp->name);
    printf("나이 : %d\n", mp->age);
    printf("성별 : %c\n", mp->gender);
    printf("키 : %.1lf\n", mp->height);

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
