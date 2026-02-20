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
    char str_1[80] = "strawberry";
    char str_2[80] = "apple";
    char *ps1 = "banana";
    char *ps2 = str_2;

    // 데이터 준비 및 입력

    // 로직 처리
    printf("최초 문자열 : %s\n", str_1);
    strcpy(str_1, str_2);
    printf("바뀐 문자열 : %s\n", str_1);

    strcpy(str_1, ps1);
    printf("바뀐 문자열 : %s\n", str_1);

    strcpy(str_1, ps2);
    printf("바뀐 문자열 : %s\n", str_1);

    strcpy(str_1, "banana");
    printf("바뀐 문자열 : %s\n", str_1);
    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/