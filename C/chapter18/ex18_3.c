/*
    제작 시간 : 0226_10:49
    유형 : 예제
    주제 : 문자 출력 함수 fputc
    문제 설명:
    - 문자열을 한문자씩 파일로 출력하기
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
    FILE *fp;
    char str[] = "banana";

    /*        입 력       */
    fp = fopen("b.txt", "w");

    /*        처 리       */
    if (fp == NULL) // ==  if(!fp)
    {
        printf("파일을 만들지 못했습니다.\n");
        return 1;
    }

    /*        출 력       */
    // printf("파일 생성");
    // int i = 0;
    // while (str[i] != '\0')
    // {
    //     fputc(str[i], fp);
    //     i++;
    // }
    // fputc('\n', fp);

    // shar str[] = "banana";
    for (int i = 0; i < (int)strlen(str) /*sizeof(str - 1)*/; i++)
    {
        fputc(str[i], fp);
    }
    fputc('\n', fp);
    fclose(fp);

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
