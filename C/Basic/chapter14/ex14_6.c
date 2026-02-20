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
    char *party[5];

    // 데이터 준비 및 입력
    party[0] = "dog";
    party[1] = "tiger";
    party[2] = "rabbit";
    party[3] = "horse";
    party[4] = "cat";

    // 로직 처리

    // 결과 출력
    for (int i = 0; i < sizeof(party) / sizeof(party[0]); i++)
    {
        printf("%s\t", party[i]);
    }
    printf("\n");

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/