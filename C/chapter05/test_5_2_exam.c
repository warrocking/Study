/*
    제작 시간 : 0223_17:36
    유형 : 연습
    주제 : 계산기 프로그램
    문제 설명: 키보드로 수식을 입력하면 계산 결과를 출ㄹ겨하는 프로그램을 작성하시오. 정수 사칙연산만 입력합니다.
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
#include <ctype.h>  // 문자 판별/변환     // isdigit, isalpha, isspace, tolower, toupper // 예: if (isdigit(c)) ...
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
    int a, b;
    char op;
    char cont = 'y';
    char line[100];
    char extra;

    while (cont == 'y' || cont == 'Y')
    {
        printf("정수 연산식 입력 (예: 3 + 5): ");
        if (!fgets(line, sizeof line, stdin))
        {
            break;
        }
        if (sscanf(line, " %d %c %d %c", &a, &op, &b, &extra) != 3)
        {
            printf("잘못된 입력입니다. (예: 3 + 5)\n");
            continue;
        }

        switch (op)
        {
        case '+':
            printf("결과: %d\n", a + b);
            break;
        case '-':
            printf("결과: %d\n", a - b);
            break;
        case '*':
            printf("결과: %d\n", a * b);
            break;
        case '/':
            if (b == 0)
            {
                printf("0으로 나눌 수 없습니다.\n");
            }
            else
            {
                printf("결과: %d\n", a / b);
            }
            break;
        default:
            printf("지원하지 않는 연산자입니다.\n");
        }
        printf("계속할까요? (y/n): ");
        if (!fgets(line, sizeof line, stdin))
        {
            break;
        }
        cont = 'n';
        for (int i = 0; line[i] != '\0'; i++)
        {
            if (!isspace((unsigned char)line[i]))
            {
                cont = line[i];
                break;
            }
        }
    }
    return 0;
}

/* 함수 정의 공간 */



