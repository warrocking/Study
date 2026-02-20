/* 문제 요약:
   - p.100
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    int kor;
    int eng;
    int mat;

    int sum;
    double avg;

    // 데이터 준비 및 입력
    printf("국어 : ");
    scanf("%d", &kor);
    printf("영어 : ");
    scanf("%d", &eng);
    printf("수학 : ");
    scanf("%d", &mat);

    // 로직 처리
    sum = kor + eng + mat;
    avg = sum / 3.0;

    // 결과 출력
    printf("총점 : %d\n", sum);
    printf("평균 : %.1lf\n", avg);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/