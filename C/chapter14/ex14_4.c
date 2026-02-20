/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char animal_1[5][10] = {
        {'d', 'o', 'g', '\0'},
        {'t', 'i', 'g', 'e', 'r', '\0'},
        {'r', 'a', 'b', 'b', 'i', 't', '\0'},
        {'h', 'o', 'r', 's', 'e', '\0'},
        {'c', 'a', 't', '\0'},
    };

    char animal_2[][10] = {"dog", "tiger", "rabbit", "horse", "cat"};
    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력
    for (int i = 0; i < 5; i++)
    {
        printf("%s\t", animal_1[i]);
    }

    printf("\n");

    for (int i = 0; i < 5; i++)
    {
        printf("%s\t", animal_2[i]);
    }

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/