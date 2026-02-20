/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화

    // 데이터 준비 및 입력

    // 로직 처리

    // 결과 출력
    printf("%s\n", "abcde");
    printf("첫 번째 문자 값 : %c\n", *("abcde"));
    printf("두 번째 문자 값 : %c\n", *("abcde" + 1));
    printf("세 번째 문자 값 : %c\n", *("abcde" + 2));
    printf("네 번째 문자 값 : %c\n", *("abcde" + 3));
    printf("네 번째 문자 값 : %c\n", *("abcde" + 3));
    printf("다섯 번째 문자 값 : %c\n", *("abcde" + 4));
    printf("여섯 번째 문자 값 : %c\n", *("abcde" + 5));

    printf("%p\n", "abcde");

    int a = 5;
    int *pa = &a;
    printf("&a : %p\n", pa);      // 포인터 변수는 주소를 값으로 한다.
    printf("a의 값 : %d\n", *pa); // pa값을 따라간 변수, 즉 a값을 출력한다.

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/