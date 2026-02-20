/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <string.h>
// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char str1[80], str2[80];
    char *resp; // 문자열이 긴 배열을 선택할 포인터

    // 데이터 준비 및 입력
    printf("2개의 과일 이름 입력 : ");
    scanf("%s%s", str1, str2);

    // 로직 처리
    /*  if (strlen(str1) > strlen(str2))
         resp = str1;
     else
         resp = str2; */
    resp = (strlen(str1) > strlen(str2)) ? str1 : str2;

    // 결과 출력
    printf("문자 1의 길이 : %d\n", strlen(str1));
    printf("문자 2의 길이 : %d\n", strlen(str2));

    printf("이름이 긴 과일은 : %s\n", resp);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/