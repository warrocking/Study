/* 문제 요약:
   -
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int num, grade;

    // 데이터 준비 및 입력
    printf("학번 입력 : ");
    scanf("%d", &num);
    getchar(); // 엔터를 먹음. 즉, 버퍼를 먹어줘서 없애줌.
    printf("학점 입력 : ");
    grade = getchar();
    printf("학번 : %d, 학점 : %c\n", num, grade);

    // 로직 처리

    // 결과 출력

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/