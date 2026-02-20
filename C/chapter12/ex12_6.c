/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int age;
    char *endptr; // 에러 처리용
    char strAge[20];
    char name[20];
    // 데이터 준비 및 입력
    printf("나이 입력 : ");
    // scanf("%d", &age);
    // fgetc(stdin);

    // fgets(strAge, sizeof(strAge), stdin);
    // age = atoi(strAge);

    fgets(strAge, sizeof(strAge), stdin);
    age = strtol(strAge, &endptr, sizeof(strAge));

    printf("이름 입력 : ");
    gets(name);

    // 로직 처리

    // 결과 출력
    printf("나이 : %d\n", age);
    printf("이름 : %s\n", name);
    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/