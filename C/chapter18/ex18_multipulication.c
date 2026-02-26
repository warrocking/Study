/*
    제작 시간 : 0226_11:07
    유형 : 과제
    주제 : 구구단을 생성해서 메모장에 넣기
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
    int count;         // 구구단수 입력 변수
    char filename[40]; // 파일 이름
    FILE *fp;          // 파일 여는 포인터

    /*        입 력       */
    printf("원하는 구구단수를 생성 후, 파일을 만들어서 구구단을 입력하는 프로그램\n");
    printf("원하는 구구단 수 : ");
    if (scanf("%d", &count) != 1)
    {
        printf("숫자만 입력하세요.\n");
        return 1;
    }
    {
        int ch;
        while ((ch = getchar()) != '\n' && ch != EOF)
        {
        }
    }
    // printf("원하는 파일 명 : ");
    // scanf("%s", filename);
    while (1)
    {
        printf("원하는 파일 명 : ");
        if (fgets(filename, sizeof filename, stdin) == NULL)
        {
            printf("파일명을 입력해야만 합니다.\n");
            return 1;
        }
        filename[strcspn(filename, "\r\n")] = '\0';
        if (filename[0] == '\0')
        {
            printf("파일명을 입력해야만 합니다.\n");
            continue;
        }
        break;
    }
    fp = fopen(filename, "w");
    if (fp == NULL)
    {
        printf("파일을 만들지 못했습니다.\n");
        return 1;
    }

    for (int i = 1; i <= 9; i++)
    {
        fprintf(fp, "%d * %d = %d\n", count, i, count * i);
    }

    /*        처 리       */

    /*        출 력       */

    /* 함수 종료 */
    fclose(fp);
    return 0;
}

/* 함수 정의 공간 */
