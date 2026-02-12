#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>

int main() {
    int value;
    printf("변환 할 숫자 : ");
    scanf_s("%d", &value);
    // 10진수
    printf("\n10진수 : %d\n", value);
    
    // 8진수
    printf("8진수 : %o\n", value);
    
    // 16진수
    printf("16진수 : %x\n", value);

    return 0;
}