/*
    제작 시간 : 0223_11:41
    유형 : 예제
    제목 : 배열과 포인터를 멤버로 갖는 구조체 발동

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
static void trim_newline(char *s);

struct profil
{
    char name[80];
    int age;
    double height;
    char *intro;
};

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    struct profil yuni;
    const size_t intro_size = 80;

    /*        입 력       */
    // strcpy(yuni.name, "서하윤");
    printf("이름 : ");
    fgets(yuni.name, sizeof(yuni.name), stdin);
    trim_newline(yuni.name);

    printf("나이 : ");
    scanf("%d", &yuni.age);

    printf("몸무게 : ");
    scanf("%lf", &yuni.height);
    // yuni.age = 17;
    // yuni.height = 164.5;
    /*        처 리       */
    yuni.intro = (char *)malloc(sizeof(char) * intro_size);
    if (yuni.intro == NULL)
    {
        return 1;
    }
    printf("자기 소개 : ");
    {
        int ch;
        while ((ch = getchar()) != '\n' && ch != EOF)
        {
        }
    }
    fgets(yuni.intro, intro_size, stdin);
    trim_newline(yuni.intro);
    /*        출 력       */
    printf("항상 행복하세요.\n");
    printf("이름 : %s\n", yuni.name);
    printf("나이 : %d\n", yuni.age);
    printf("키 : %.1lf\n", yuni.height);
    printf("자기소개 : %s\n", yuni.intro);
    free(yuni.intro);
    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
static void trim_newline(char *s) // 입력버퍼 제거 공간
{
    size_t len;
    if (s == NULL)
    {
        return;
    }
    len = strlen(s);
    if (len > 0 && s[len - 1] == '\n')
    {
        s[len - 1] = '\0';
    }
}
