/*
    제작 시간 : 0225_20:10
    유형 : 연습
    주제 : p540 도전 실전 예제
    문제 설명:
    - 학생 5명의 국어, 영어, 수학 점수를 입력해 총점, 평균 학점을 구하고 총점 순으로 정렬해 출력합니다.
    - 학점은 평균이 90점 이상이면 A, 80점 이상이면 B, 70점 이상이면 C, 그 외는 F로 평가합니다.
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
#define STUDENT_COUNT 5
#define SUBJECT_COUNT 3

// 구조 선언 (typedef / struct / enum / union ...)
typedef struct Student
{
    int num;       // 학번
    char name[80]; // 이름
    int score[SUBJECT_COUNT]; // 0번 국어 , 1번 영어 , 2번 수학
    double avg;    // 평균
    char grade;    // 학점
} student;

// 전역 변수

// 함수 프로토타입
static int read_student(student *s);
static void calc_avg_grade(student *s);
static void print_header(void);
static void print_list(const student *list, size_t count);
static int compare_avg_desc(const void *a, const void *b);

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    student *list = (student *)malloc(sizeof(*list) * STUDENT_COUNT);
    if (!list)
    {
        printf("메모리 할당 실패\n");
        return 1;
    }

    /*        입 력       */
    for (int i = 0; i < STUDENT_COUNT; i++)
    {
        if (!read_student(&list[i]))
        {
            printf("입력 오류\n");
            free(list);
            return 1;
        }
    }

    /*        처 리       */
    for (int i = 0; i < STUDENT_COUNT; i++)
    {
        calc_avg_grade(&list[i]);
    }
    /*        출 력       */
    printf("# 정렬 전 데이터.........\n");
    print_list(list, STUDENT_COUNT);

    // 평균 내림차순 정렬
    qsort(list, STUDENT_COUNT, sizeof(list[0]), compare_avg_desc);

    printf("# 정렬 후 데이터.........\n");
    print_list(list, STUDENT_COUNT);

    /* 함수 종료 */
    free(list);
    return 0;
}

/* 함수 정의 공간 */
static int read_student(student *s)
{
    printf("학번 : ");
    if (scanf("%d", &s->num) != 1)
    {
        return 0;
    }
    printf("이름 : ");
    if (scanf("%79s", s->name) != 1)
    {
        return 0;
    }
    printf("국어 : ");
    if (scanf("%d", &s->score[0]) != 1)
    {
        return 0;
    }
    printf("영어 : ");
    if (scanf("%d", &s->score[1]) != 1)
    {
        return 0;
    }
    printf("수학 : ");
    if (scanf("%d", &s->score[2]) != 1)
    {
        return 0;
    }
    printf("\n");
    return 1;
}

static void calc_avg_grade(student *s)
{
    s->avg = (s->score[0] + s->score[1] + s->score[2]) / 3.0;

    if (s->avg >= 90.0)
        s->grade = 'A';
    else if (s->avg >= 80.0)
        s->grade = 'B';
    else if (s->avg >= 70.0)
        s->grade = 'C';
    else
        s->grade = 'F';
}

static void print_header(void)
{
    printf("학번\t이름\t국어\t영어\t수학\t평균\t학점\n");
}

static void print_list(const student *list, size_t count)
{
    print_header();
    for (size_t i = 0; i < count; i++)
    {
        printf("%d\t %s\t %d\t %d\t %d\t %.1lf\t %c\n",
               list[i].num,
               list[i].name,
               list[i].score[0],
               list[i].score[1],
               list[i].score[2],
               list[i].avg,
               list[i].grade);
    }
}

static int compare_avg_desc(const void *a, const void *b)
{
    const student *sa = (const student *)a;
    const student *sb = (const student *)b;
    if (sa->avg < sb->avg)
        return 1;
    if (sa->avg > sb->avg)
        return -1;
    return 0;
}
