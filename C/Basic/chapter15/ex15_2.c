/*
    문제 요약 : 이중 포인터를 사용한 포인터 교환

    문제 설명
    - 2중 포인터를 사용하는 예시 -> 문자열 상수를 스왑할 때
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
void swap_ptr(char **ppa, char **ppb)
{
    char *temp;
    temp = *ppa;
    *ppa = *ppb;
    *ppb = temp;
}

int main(void)
{
    // 변수 선언 및 초기화
    char *pa = "success";
    char *pb = "failure";

    // 데이터 준비 및 입력
    printf("pa -> %s, pb -> %s\n", pa, pb);

    // 로직 처리
    swap_ptr(&pa, &pb);

    // 결과 출력
    printf("pa -> %s, pb -> %s\n", pa, pb);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/