/*
    제작 시간 : 0226_11:45
    유형 : 예제
    주제 : 텍스트파일과 바이너리 파일
    문제 설명:
    - 파일의 형태와 개방 모드가 다른 경우
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
    int ary[10] = {13, 10, 13, 13, 10, 26, 13, 10, 13, 10};
    int res;

    /*        입 력       */
    fp = fopen("a.txt", "wb");
    if (!fp)
    {
        perror("open");
        return 1;
    }

    for (int i = 0; i < 10; i++)
    {
        fwrite(&ary[i], sizeof(int), 1, fp); // int 그대로 저장
    }
    fclose(fp);

    fp = fopen("a.txt", "rb");
    if (!fp)
    {
        perror("open");
        return 1;
    }

    int x;
    while (fread(&x, sizeof(int), 1, fp) == 1)
    {
        printf("%4d", x);
    }
    fclose(fp);

    return 0;
}

/* 함수 정의 공간 */
