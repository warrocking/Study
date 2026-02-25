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

// 구조 선언 (typedef / struct / enum / union ...)
typedef struct Student
{
    int num;       // 학번
    char name[80]; // 이름
    int score[3];  // 0번 국어 , 1번 영어 , 2번 수학
    double avg;    // 평균
    char grade;    // 학점
} student;

// 전역 변수

// ------ 끝 ----------

/* 메인 함수 정의 */
int main(void)
{
    /* 변수 선언 및 초기화 */
    student student_before[5];
    student student_after[5];
    student max; // 최고 점수 학생 정보 저장
    /*        입 력       */
    for (int i = 0; i < 5; i++)
    {
        printf("학번 : ");
        scanf("%d", &student_before[i].num);
        printf("이름 : ");
        scanf("%s", student_before[i].name);
        printf("국어 : ");
        scanf("%d", &student_before[i].score[0]);
        printf("영어 : ");
        scanf("%d", &student_before[i].score[1]);
        printf("수학 : ");
        scanf("%d", &student_before[i].score[2]);

        printf("\n");
    }

    /*        처 리       */
    for (int i = 0; i < sizeof(student_before) / sizeof(student); i++)
    {
        student_before[i].avg = (student_before[i].score[0] + student_before[i].score[1] + student_before[i].score[2]) / 3.0;

        if (student_before[i].avg >= 90.0)
            student_before[i].grade = 'A';
        else if (student_before[i].avg >= 80.0)
            student_before[i].grade = 'B';
        else if (student_before[i].avg >= 70.0)
            student_before[i].grade = 'C';
        else
            student_before[i].grade = 'F';
    }
    /*        출 력       */
    printf("# 정렬 전 데이터.........\n");
    for (int i = 0; i < sizeof(student_before) / sizeof(student_before[0]); i++)
    {
        printf("학번\t이름\t국어\t영어\t수학\t평균\t학점\n");
        printf("%d\t %s\t %d\t %d\t %d\t %.1lf\t %c\n",
               student_before[i].num,
               student_before[i].name,
               student_before[i].score[0],
               student_before[i].score[1],
               student_before[i].score[2],
               student_before[i].avg,
               student_before[i].grade);
    }
    // 정렬용 배열 복사
    for (int i = 0; i < sizeof(student_before) / sizeof(student_before[0]); i++)
    {
        student_after[i] = student_before[i];
    }

    // 평균 내림차순 정렬(선택 정렬)
    for (int i = 0; i < sizeof(student_after) / sizeof(student_after[0]); i++)
    {
        int max_idx = i;
        for (int j = i + 1; j < sizeof(student_after) / sizeof(student_after[0]); j++)
        {
            if (student_after[j].avg > student_after[max_idx].avg)
            {
                max_idx = j;
            }
        }
        if (max_idx != i)
        {
            student temp = student_after[i];
            student_after[i] = student_after[max_idx];
            student_after[max_idx] = temp;
        }
    }
    printf("# 정렬 후 데이터.........\n");
    for (int i = 0; i < sizeof(student_after) / sizeof(student_after[0]); i++)
    {
        printf("학번\t이름\t국어\t영어\t수학\t평균\t학점\n");
        printf("%d\t %s\t %d\t %d\t %d\t %.1lf\t %c\n",
               student_after[i].num,
               student_after[i].name,
               student_after[i].score[0],
               student_after[i].score[1],
               student_after[i].score[2],
               student_after[i].avg,
               student_after[i].grade);
    }

    /* 함수 종료 */
    return 0;
}

/* 함수 정의 공간 */
