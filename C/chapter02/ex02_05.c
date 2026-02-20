/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 선언
    int value;

    // 입력
    printf("변환 할 숫자 : ");
    scanf_s("%d", &value);

    // 처리

    // 출력
    // 10진수
    printf("\n10진수 : %d\n", value);

    // 8진수
    printf("8진수 : %o\n", value);

    // 16진수
    printf("16진수 : %x\n", value);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/