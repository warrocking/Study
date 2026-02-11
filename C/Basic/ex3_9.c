// "Gcc" 컴파일러 기준

#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

int main()
{
    int a, b;
    float c;
    char d;

    printf("1_1. 정수(int) a를 입력하세요: ");
    scanf("%d", &a);
    printf("1_2. 정수(int) b를 입력하세요: ");
    scanf("%d", &b);
    printf("2. 실수(float)를 입력하세요: ");
    scanf("%f", &c);

    // 중요: 숫자 입력 후 남은 엔터(개행 문자)를 무시하기 위해 %c 앞에 공백을 추가합니다.
    printf("3. 문자(char) 하나를 입력하세요: ");
    scanf(" %c", &d);

    printf("\n--- 입력 결과 ---\n");
    printf("정수 a: %d\n", a);
    printf("정수 b: %d\n", b);
    printf("정수의 합 : %d\n", a + b);
    
    printf("실수 : %f\n", b);
    printf("문자: %c\n", c);

    return 0;
}