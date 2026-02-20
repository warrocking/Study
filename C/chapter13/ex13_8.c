/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언
int *sum(int a, int b) // int형 변수의 주소를 반환하는 주소.
{
    static int res; // 정적 지역 변수
    res = a + b;
    return &res; // 정적 지역 변수의 주소 반환
}

int main(void)
{
    // 변수 선언 및 초기화
    int *resp; // 반환값을 저장한 포인터 result pointer

    // 데이터 준비 및 입력

    // 로직 처리
    resp = sum(10, 20); // 반환된 주소는 resp에 저장
    // 왼쪽 값 : 포인터  ==  오른쪽 값 : 포인터

    // 결과 출력
    printf("두 정수의 합 : %d", *resp); // resp가 가르키는 변수값 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/