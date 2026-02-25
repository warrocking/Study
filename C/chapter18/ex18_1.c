/*
    제작 시간 : 0225_17:01
    유형 : 예제
    주제 : 파일 개방과 입출력
    문제 설명: 파일을 열고 닫는 프로그램
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
    FILE *fp;

    /*        입 력       */
    fp = fopen("a.txt", "r");

    /*        처 리       */
    if (fp == NULL)
    {
        printf("파일이 열리지 않았습니다.\n");
        return 1;
    }

    printf("파일이 열렸습니다.\n");

    int ch;
    char buf[1024];
    size_t n;
    while ((n = fread(buf, 1, sizeof buf, fp)) > 0)
    {
        fwrite(buf, 1, n, stdout);
    }

    // char buf[256];
    // while (fgets(buf, sizeof buf, fp) != NULL)
    // {
    //     fputs(buf, stdout);
    // }

    // int ch;
    // while ((ch = fgetc(fp)) != EOF)
    // {
    //     putc(ch, stdout);
    // }
    fclose(fp);

    /*        출 력       */

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
