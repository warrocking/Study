/* 문제 요약:
   - 여러 개의 1차원 배열을 2차원 배열처럼 사용하기
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int array1[4] = {1, 2, 3, 4};
    int array2[4] = {5, 6, 7, 8};
    int array3[4] = {9, 10, 11, 12};
    int *party[3] = {array1, array2, array3};

    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            printf("%d\t", party[i][j]);
        }
        printf("\n");
    }

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/