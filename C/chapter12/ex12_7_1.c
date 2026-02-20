/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char str[80] = "apple jam";
    char *ps = "banana";

    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력
    puts(str);         // 마지가 엔터 포함
    fputs(ps, stdout); // 마지감 엔터 미 포함.
    puts("milk");

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/