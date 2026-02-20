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
    int arr[2][2] = {
        {1, 2},
        {3, 4}}; // 선언과 동시에 초기화
    int cnt = 1;
    // 데이터 준비 및 입력

    // 로직 처리
    for (int x = 0; x < 2; x++)
    {
        for (int y = 0; y < 2; y++)
        {
            printf("arr[%d][%d] = %d\n", x, y, arr[x][y]);
        }
        printf("\n");
    }

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/