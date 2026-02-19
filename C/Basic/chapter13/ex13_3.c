/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언

int a;
void assign1()
{
    a = 10;
}
void assign2()
{
    int a = 10;
}
int main(void)
{
    // 변수 선언 및 초기화

    // 데이터 준비 및 입력
    printf("함수 호출 전 a값 == : %d\n", a);
    assign1();
    assign2();

    // 로직 처리

    // 결과 출력
    printf("함수 호출 후 a의 값 : %d\n", a);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/