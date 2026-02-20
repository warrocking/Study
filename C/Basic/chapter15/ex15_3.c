/*
    문제 요약 : 포인터 배열의 값을 출력하는 함수

    문제 설명
    -
    -
    -
    -
    -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언
void print_str(char **pps, int cnt)
{
    for (int i = 0; i < cnt; i++)
    {
        printf("%s\n", pps[i]);
    }
    printf("\n");
}

int main(void)
{
    // 변수 선언 및 초기화
    char *ptr_ary[] = {
        "eagle",
        "tiger",
        "lion",
        "squirrel"};
    int count;
    // 데이터 준비 및 입력
    count = sizeof(ptr_ary) / sizeof(ptr_ary[0]);

    // 로직 처리
    print_str(ptr_ary, count);

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/