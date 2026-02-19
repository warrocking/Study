/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언
void assign()
{
    int a;
    a = 10;
    printf("assign 함수 a : %d\n", a);
}
int main(void)
{
    // 변수 선언 및 초기화
    int a = 0; // C에서 auto는 저장 클래스 지정자로, **블록(scope) 안 지역 변수의 “자동 저장 기간”**을 뜻함.즉 스택에 올라갔다가 블록을 벗어나면 사라지는 변수라는 의미인데, C에서는 이게 기본값이라서 auto를 써도 의미가 같다.

    // 데이터 준비 및 입력
    assign();
    printf("main 함수 a : %d\n", a);
    // 로직 처리

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/
