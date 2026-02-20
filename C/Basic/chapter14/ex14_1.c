/* 문제 요약:
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
    int score[3][4];
    int total;
    double avg;

    // 데이터 준비 및 입력
    for (int x = 0; x < 3; x++)
    {
        printf("4과목 점수 입력\n");
        for (int y = 0; y < 4; y++)
        {
            printf("score[%d][%d] : ", x, y);
            scanf("%d", &score[x][y]);
        }
        printf("\n");
    }

    // 로직 처리

    // 결과 출력
    for (int x = 0; x < 3; x++)
    {
        total = 0;
        for (int y = 0; y < 4; y++)
        {
            total += score[x][y];
        }
        avg = (double)total / 4.0;
        printf("총점 : %d, 평균 : %.2f\n", total, avg);
    }

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/