/*
    문제 요약 : 학생 3명의 네 과목 총점과 평균을 구하는 프로그램

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

int main(void)
{
    // 변수 선언 및 초기화
    int arr[3][4];
    int cnt = 1;

    // 데이터 준비 및 입력

    // 로직 처리
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            arr[i][j] = cnt++;
            // cnt++;
            printf("arr[%d][%d] = %d\n", i, j, arr[i][j]);
        }
    }
    printf("\n\n");
    // 결과 출력
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            printf("%5d", arr[i][j]);
        }
        printf("\n");
    }
    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/