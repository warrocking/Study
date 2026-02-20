/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언
void add_by_pointer(int *pa, int *pb, int *pr)
{
    *pr = *pa + *pb;
}

int main(void)
{
    // 변수 선언 및 초기화
    int a = 10;
    int b = 20;
    int res = 0;

    // 데이터 준비 및 입력

    // 로직 처리
    add_by_pointer(&a, &b, &res);

    // 결과 출력
    printf("%d\n", res);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/