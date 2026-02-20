/* 문제 요약:
   - unsigned를 잘못 사용한 경우
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    unsigned int a;

    // 데이터 준비 및 입력

    // 처리

    // 출력
    a = 4294967295;
    printf("%d\n", a);
    a = -1;
    printf("%u\n", a);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/