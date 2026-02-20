/* 문제 요약:
   - 공백이나 제어 문자의 입력
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char ch1, ch2;

    // 데이터 준비 및 입력
    scanf(" %c %c", &ch1, &ch2);

    // 로직 처리

    // 결과 출력
    printf("[%c%c]\n", ch1, ch2);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/