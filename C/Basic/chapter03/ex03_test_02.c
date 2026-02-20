/* 문제 요약:
   - 키보드로 문자를 입력해 아스키 코드 값을 출력하는 프로그램이 완성되도록 빈칸에 알맞은 코드를 적으세요
   (어떤 문자가 입력될지는 실행할 떄 결정합니다.)
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char ch;

    // 데이터 준비 및 입력
    printf("문자 입력 : ");
    scanf("%c", &ch);

    // 로직 처리

    // 결과 출력
    printf("%c 문자의 아스키 코드 값은 %d입니다\n", ch, ch);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/