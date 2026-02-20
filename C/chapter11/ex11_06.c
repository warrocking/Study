/* 문제 요약:
   - getchar 함수를 사용한 문자열 입력
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언
void my_gets(char *str, int size)
{
    int ch;
    int i = 0;
    ch = getchar();
    while ((ch != '\n') && (i < size - 1))
    {
        str[i] = ch;
        i++;
        ch = getchar();
    }
    str[i] = '\0';
}

int main(void)
{
    // 변수 선언 및 초기화
    char str[7]; // 6자 입력 받음.

    // 데이터 준비 및 입력
    my_gets(str, sizeof(str));

    // 로직 처리

    // 결과 출력
    printf("입력한 문자열 : %s\n", str);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/