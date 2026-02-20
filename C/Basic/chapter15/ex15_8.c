/*
    문제 요약 : 함수 포인터로 원하는 함수를 호출하는 프로그램

    문제 설명
    - 델리게이트와 연계된 내용이니 중요.!
    -
    -
    -
    -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언
void func(int (*fp)(int, int)) // fp의 의미 : function point , 즉 함수 포인터
{
    int a, b;
    int res;
    printf("두 정수를 입력하시오 : ");
    scanf("%d %d", &a, &b);
    res = fp(a, b);
    printf("결과값 : %d\n", res);
}
int sum(int a, int b)
{
    return (a + b);
}
int mul(int a, int b)
{
    return (a * b);
}
int max(int a, int b)
{
    return (a > b ? a : b);
}
int main(void)
{
    // 변수 선언 및 초기화
    int sel;

    // 데이터 준비 및 입력
    printf("01 두 정수의 합\n");
    printf("02 두 정수의 곱\n");
    printf("03 두 정수 중에서 큰 값 계산\n");

    printf("원하는 연산을 선택하세요. : ");
    scanf("%d", &sel);

    // 로직 처리
    switch (sel)
    {
    case 1:
        func(sum);
        break;
    case 2:
        func(mul);
        break;
    case 3:
        func(max);
        break;
    default:
        printf("잘못된 선택입니다.\n");
        break;
    }

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/