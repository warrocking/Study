#include <stdio.h>

int main() 
{
    int a = 0;
    int b = 0;

    printf("첫 번쨰 숫자 입력 : ");
    scanf("%d", &a);
    printf("두 번쨰 숫자 입력 : ");
    scanf("%d", &b);

    if(a>b)
    {
        b= a;
    }
    else
    {
        a = b;
    }
    printf("a : %d\n", a);
    printf("b : %d\n", b);
    return 0;
}
