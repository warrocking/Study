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
    printf("apple이 저장된 시작 주소 값 : %p\n", "apple");
    printf("두 번째 문자의 주소 값 : %p\n", "apple" + 1);

    printf("첫 번째 문자 : %c\n", *"apple");
    printf("두 번째 문자 : %c\n", *("apple" + 1));

    printf("알파벳 상 첫번째 문장 다음 단어 : %c\n", *"apple" + 1);

    printf("배열로 표현한 세 번쨰 문자 : %c\n", "apple"[2]);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/