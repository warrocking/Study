/* 문제 요약:
   - 대문자를 소문자로 변경
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char small;
    char cap = 'B';

    // 데이터 준비 및 입력

    // 로직 처리
    if ((cap >= 'A') && (cap <= 'Z'))
    {
        small = cap + /*32*/ ('a' - 'A');
    }

    // 결과 출력
    printf("대문자 : %c\n", cap);
    printf("소문자 : %c\n", small);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/