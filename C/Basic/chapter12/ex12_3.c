/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char str[80];

    // 데이터 준비 및 입력
    printf("문자열 입력 : ");
    /* scanf("%s", str);
    printf("첫 번쨰 단어 : %s\n", str);

    scanf("%s", str);
    printf("버퍼에 남아 있는 두 번쨰 단어 : %s\n", str); */

    // gets_s(str, sizeof(str));
    fgets(str, sizeof(str), stdin);
    printf("get 사용한 출력 : %s\n", str);

    // 로직 처리

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/