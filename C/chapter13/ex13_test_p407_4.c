/* 문제 요약:
   -  p.408
   2개의 전역 변수에 값을 입력하고 교환한 후 출력하는 프로그램을 작성한다.
   입력, 교환, 출력 작업은 다음에 제시한 함수 원형을 지켜 작성한다.
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>
int a, b;
// 함수 선언
void input_data(int *pa, int *pb)
{
    printf("두 정수 입력\n");
    printf("a 입력 : ");
    scanf("%d", pa);
    printf("b 입력 : ");
    scanf("%d", pb);
    // scanf("%d %d", &a, &b);
}
void swap_data()
{
    int temp;
    temp = a;
    a = b;
    b = temp;
}
void printf_data(int a, int b)
{
    printf("두 정수 출력 : %d, %d\n", a, b);
}

int main(void)
{
    // 변수 선언 및 초기화

    // 데이터 준비 및 입력

    // 로직 처리
    input_data(&a, &b);
    swap_data();
    printf_data(a, b);

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/