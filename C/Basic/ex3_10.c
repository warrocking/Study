#include <stdio.h>
#define _CRT_SECURE_NO_WARNINGS

int main() {
    
    int age=0;
    double height=0;

    printf("나이 : ");
    scanf("%d", &age);
    printf("키 : ");
    scanf("%lf", &height);

    printf("나이는 %d살이며 키는 %.1lfcm입니다.\n", age, height);
    return 0;

}