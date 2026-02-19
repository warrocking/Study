/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <string.h>
// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char str[20] = "mango tree";

    // 데이터 준비 및 입력
    strncpy(str, "apple-line", 6);

    // 로직 처리

    // 결과 출력
    printf("%s\n", str);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/