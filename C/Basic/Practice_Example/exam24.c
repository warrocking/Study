/* 문제 요약:
   -  문자열을 입력받고 출력을 해보세요.

단 입력받은 문자열의 역순으로 출력해 봅시다.﻿

#include<string.h>

int len = strlen(str); 

Hello

-------------------------

olleH
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char str[80];
    char str_reverse[80];

    // 데이터 준비 및 입력
    printf("문자열을 입력하시오 : ");
    scanf("%s", str);

    // 로직 처리
    int len = strlen(str);
    for (int i = 0; i < len; i++)
    {
        str_reverse[i] = str[len - i - 1];
    }

    // 결과 출력
    printf("뒤집어진 문자열 : %s\n", str_reverse);

    // 함수종료
    return 0;

    /* har str1[80];
    printf("입력 : ");
    scanf("%s", str1);
    int len = strlen(str1);
    for (int i = len; i >= 0; i--)
    {
        printf("%c", str1[i]);
    }

    return 0; */
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/