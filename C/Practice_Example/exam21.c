/* 문제 요약:
   - main에서  두정수 int a = 10, b = 20

   swap(a, b) ==> 수정하세요.

   swap함수를 통해 실제 값이 바뀌도록 구현하세요.

*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언
void swap(int *a, int *b)
{
    int temp;
    temp = *a;
    *a = *b;
    *b = temp;
}

int main(void)
{
    // 선언
    int a = 10;
    int b = 20;

    // 입력
    printf("swap 전 a, b값\n");
    printf("a : %d\n", a);
    printf("b : %d\n", b);

    // 처리
    swap(&a, &b);

    // 출력
    printf("swap 후 a, b값\n");
    printf("a : %d\n", a);
    printf("b : %d\n", b);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/