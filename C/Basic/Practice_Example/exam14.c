#include <stdio.h>

int plus(int x, int y);
int minus(int x, int y);
double mul(int x, int y);
double div(int x, int y);
double quo(int x, int y);
int main()
{
    int a, b;
    printf("a 입력 : ");
    scanf("%d", &a);
    printf("b 입력 : ");
    scanf("%d", &b);

    printf("각 종류의 사칙연산 결과\n\n");

    printf("합 연산 : %d\n", plus(a, b));
    printf("차 연산 : %d\n", minus(a, b));
    printf("곱 연산 : %.2lf\n", mul(a, b));
    printf("나누기 연산 : %.2lf\n", div(a, b));
    printf("나머지 연산 : %.2lf\n", quo(a, b));

    return 0;
}
int plus(int x, int y)
{
    int value = x+y;
    return value;
}
int minus(int x, int y)
{
    int value;
    if(x>y)
        value = x-y;
    else
        value = y-x;
    return value;
}
double mul(int x, int y)
{
    double value;
    value = x*y;
    return value;
}
double div(int x, int y)
{
    double value;//몫
    
    if(x>y)
        value = x/y;
    else
        value = y/x;
    return value;

}
double quo(int x, int y)
{
    double value;//몫
    
    if(x>y)
        value = x%y;
    else
        value = y%x;
    return value; 
}