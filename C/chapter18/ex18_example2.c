/*
    제작 시간 : 0226_10:03
    유형 : 과제
    주제 : 개인적으로 만드는 파일 입출력 코드
    문제 설명:
    - 1. 파일 명 입력하고
    - 2-1. 파일명에 똑같은 파일이 있다면 오픈
    - 2-2. 파일이 없다면 입력한 파일명으로 파일 생성할 건지 물어보고( y/n)
            파일 생성하기
    - 3. 파일을 생성한 후 파일 안에 넣을 내용 작성하기.
    - 4. 파일 내용을 진짜 저장할 건지 물어보기(y/n)
    - 5-1. y 라면 파일에 작성한 내용 저장하기
    - 5-2. n 라면 파일에 작성한 내용 넣지않기.
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
    char filename[256];
    char line[256];
    FILE *fp = NULL;

    /*        입 력       */
    printf("파일명 입력: ");
    if (fgets(filename, sizeof filename, stdin) == NULL)
    {
        return 1;
    }
    filename[strcspn(filename, "\r\n")] = '\0';
    if (filename[0] == '\0')
    {
        printf("파일명이 비어 있습니다.\n");
        return 1;
    }

    /*        처 리       */
    fp = fopen(filename, "r");
    if (fp != NULL)
    {
        printf("파일이 존재합니다. 열었습니다.\n");
        fclose(fp);
    }
    else
    {
        char answer[8];
        printf("파일이 없습니다. 생성할까요? (y/n): ");
        if (fgets(answer, sizeof answer, stdin) == NULL)
        {
            return 1;
        }
        if (answer[0] != 'y' && answer[0] != 'Y')
        {
            printf("파일을 생성하지 않았습니다.\n");
            return 0;
        }

        fp = fopen(filename, "w");
        if (fp == NULL)
        {
            perror("파일 생성 실패");
            return 1;
        }
        fclose(fp);
        printf("파일을 생성했습니다.\n");
    }

    printf("파일에 넣을 내용을 입력하세요. 한 줄에 END 입력 시 종료됩니다.\n");
    char *content = NULL;
    size_t cap = 0;
    size_t len = 0;

    while (fgets(line, sizeof line, stdin) != NULL)
    {
        if (strcmp(line, "END\n") == 0 || strcmp(line, "END\r\n") == 0 || strcmp(line, "END") == 0)
        {
            break;
        }

        size_t line_len = strlen(line);
        if (len + line_len + 1 > cap)
        {
            size_t newcap = (cap == 0) ? 512 : cap * 2;
            while (newcap < len + line_len + 1)
            {
                newcap *= 2;
            }
            char *tmp = (char *)realloc(content, newcap);
            if (tmp == NULL)
            {
                printf("메모리 부족\n");
                free(content);
                return 1;
            }
            content = tmp;
            cap = newcap;
        }

        memcpy(content + len, line, line_len);
        len += line_len;
        content[len] = '\0';
    }

    /*        출 력       */
    {
        char answer[8];
        printf("내용을 저장할까요? (y/n): ");
        if (fgets(answer, sizeof answer, stdin) == NULL)
        {
            free(content);
            return 1;
        }

        if (answer[0] == 'y' || answer[0] == 'Y')
        {
            fp = fopen(filename, "w");
            if (fp == NULL)
            {
                perror("파일 열기 실패");
                free(content);
                return 1;
            }
            if (len > 0)
            {
                fwrite(content, 1, len, fp);
            }
            fclose(fp);
            printf("저장했습니다.\n");
        }
        else
        {
            printf("저장하지 않았습니다.\n");
        }
    }
    free(content);

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
