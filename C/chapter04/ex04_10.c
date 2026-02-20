/*
    문제 요약 : 복합 대입 연산자의 사용 예

    문제 설명
    - a에 20을 더하고, res에 (b + 10)을 곱한 값을 대입한다.
    - 출력 결과로 a와 res의 최종 값을 확인한다.

    문제 관련 지식
    - 복합 대입 연산자 `+=`, `*=`는 각각 `a = a + x`, `a = a * x`의 축약형이다.
    - `*=`의 오른쪽은 하나의 식으로 계산된 뒤 왼쪽에 곱해진다.
    - 연산 우선순위에 의해 `b + 10`이 먼저 계산된다.
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int a = 10;
    int b = 20;
    int res = 2;

    // 데이터 준비 및 입력
    a += 20;

    res *= b + 10; // b(20)+10=30 -> res(2) = res(2) * 30

    // 로직 처리

    // 결과 출력
    printf("a : %d\n", a);
    printf("res : %d\n", res);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/