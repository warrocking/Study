#include <stdio.h>

int main()
{
    int a;
    double b;
    char c;
    char *str = "Hello World!";
    printf("int형 변수의 주소 : %p\n", &a);
    printf("double형 변수의 주소 : %p\n", &b);
    printf("global형 변수의 주소 : %u, %p\n", &c, &c);
    printf("문자열 변수의 주소 : %u, %p\n", str, str);

    return 0;
}