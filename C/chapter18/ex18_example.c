/*
    제작 시간 : 0226_09:32
    유형 : 예제
    주제 : 수업 내용 따라 쓰기
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
    FILE *fptr = fopen("a.txt", "r");

    /*        입 력       */
    if (fptr == NULL)
    {
        // printf("%s\n\n", "파일이 없습니다.");
        fprintf(stderr, "%s\n\n", "파일이 없다");
        return 1;
    }

    /*        처 리       */
    int value = 0;
    fscanf(stdin, "%d", &value);
    fprintf(stdout, "%s\r\n", fptr);
    fprintf(stderr, "%s\r\n", fptr);

    /*        출 력       */
    while (1)
    {
        char ch = fgetc(fptr);
        if (ch == EOF)
        {
            break;
        }
        putc(ch, stdout); // printf 같은거 / stdout : 표준 출력 (모니터 같은거)
    }
    /* 함수 종료 */
    fclose(fptr);
    return 0;
}

/* 함수 정의 공간 */
