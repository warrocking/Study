#include <stdio.h>

int main()
{
    int a = 10;
    int b = 20;
    int res = 2;

    a += 20;

    res *= b+10; // b(20)+10=30 -> res(2) = res(2) * 30

    printf("a : %d\n", a);
    printf("res : %d\n", res);

    return 0;

}