/* 문제 요약:
   - getchar 함수와 putchar 함수 사용
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int ch;

    // 데이터 준비 및 입력
    ch = getchar();
    printf("입력한 문자 : ");

    // 로직 처리
    putchar(ch);
    putchar('\n');
    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/