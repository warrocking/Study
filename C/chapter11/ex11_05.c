/* 문제 요약:
   - 입력 문자의 아스키 코드 값을 출력하는 프로그램.
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int res;
    char ch; // 버퍼

    // 데이터 준비 및 입력
    printf("문자를 입력하면 아스키코드를 출력하는 프로그램이 반복합니다.\n끝내고 싶다면 ctrl + c(vscode 기준) or ctrl + z(visual studio기준)를 누르세요.\n");
    // 로직 처리
    while (1)
    {
        res = scanf("%c", &ch);
        if (res == -1)
            break;

        printf("%c 문자의 아스키 코드 값은 %d입니다\n", ch, ch);
    }

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/