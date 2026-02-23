/*
    제작 시간 : 0223_10:44
    유형 : 예제
    제목 : 3개의 문자열을 저장하기 위한 동적 할당

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

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    char temp[80];
    char *str[3];
    char *str2 = "hi";
    char *str3 = "hi";
    int a = 10;
    int b = 10;
    /*        입 력       */
    for (int i = 0; i < sizeof(str) / sizeof(str[0]); i++)
    {
        printf("문자열을 입력하시오 : ");
        // gets(temp);
        fgets(temp, sizeof(temp), stdin);
        str[i] = (char *)malloc(strlen(temp) + 1); // +1의 의미 : '\0'(NULL) 문자의 공간확보
        strcpy(str[i], temp);
    }

    /*        처 리       */

    /*        출 력       */

    printf("str 주소 : %p\n", str);
    printf("str[0] 주소 : %p\n", str[0]);
    printf("str[1] 주소 : %p\n", str[1]);
    printf("str[2] 주소 : %p\n", str[2]);
    printf("str2 주소 : %p\n", str2);
    printf("str3 주소 : %p\n", str3);
    printf("a 의 주소 : %p\n", &a);
    printf("b 의 주소 : %p\n", &b);

    printf("\n");
    for (int i = 0; i < sizeof(str) / sizeof(str[0]); i++)
    {
        printf("%s", str[i]);
    }
    // free
    for (int i = 0; i < sizeof(str) / sizeof(str[0]); i++)
    {
        free(str[i]);
    }
    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
