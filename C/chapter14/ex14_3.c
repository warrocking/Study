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
    char animal[5][20];
    int count = 0;

    // 데이터 준비 및 입력
    count = sizeof(animal) / sizeof(animal[0]);
    for (int i = 0; i < count; i++)
    {
        scanf("%s", animal[i]); // 2번 동작
    }
    // 로직 처리

    // 결과 출력
    for (int i = 0; i < count; i++)
    {
        printf("%s\t", animal[i]);
    }
    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/