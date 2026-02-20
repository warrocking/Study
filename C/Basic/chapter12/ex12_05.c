/* 문제 요약:
   - fgets 함수의 문자열 입력 방법
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

    // 데이터 준비 및 입력
    printf("공백이 포함된 문자열 입력 : ");
    fgets(str, sizeof(str), stdin);

    // 로직 처리

    // 결과 출력
    printf("입력된 문자열은 %s입니다.\n", str);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/