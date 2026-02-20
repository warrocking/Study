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
    char str1[80] = "pear";
    char str2[80] = "peach";

    // 데이터 준비 및 입력

    // 로직 처리
    if (strcmp(str1, str2) > 0)
    {
        printf("%s\n", str1);
    }
    else if (strcmp(str1, str2) == 0)
    {
        printf("둘의 길이는 같다.\n");
    }
    else
    {
        printf("%s\n", str2);
    }

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/