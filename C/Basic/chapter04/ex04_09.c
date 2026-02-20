/*
    문제 요약 : sizeof 연산자의 사용 예

    문제 설명
    - sizeof의 반환 타입은 size_t(부호 없는 정수 타입)이다.
    - size_t 출력 서식 지정자는 %zu가 맞다.
    - ssize_t는 POSIX의 부호 있는 크기 타입으로, 실패 시 -1 같은 값을 표현할 때 쓴다.
    - ssize_t 출력 서식 지정자는 %zd이다.
    - 따라서 sizeof 값은 %zu로 출력하는 것이 정석이다.
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
    double b = 3.4;

    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력
    /*
    // 옛날 방식
    // printf("int형 변수의 크기 : %d\n", sizeof(a));
    // printf("double형 변수의 크기 : %d\n\n", sizeof(b));

    // printf("정수형 상수의 크기 : %d\n", sizeof(10));
    // printf("수식의 결과값의 크기 : %d\n", sizeof(1.5+3.4));

    // printf("char 자료형의 크기 : %d\n", sizeof(char));

    */
    // 최신 방식
    printf("int형 변수의 크기 : %zd\n", sizeof(a));
    printf("double형 변수의 크기 : %zd\n\n", sizeof(b));

    printf("정수형 상수의 크기 : %zd\n", sizeof(10));
    printf("수식의 결과값의 크기 : %zd\n", sizeof(1.5 + 3.4));

    printf("char 자료형의 크기 : %zd\n", sizeof(char));
    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/
