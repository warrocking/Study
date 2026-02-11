#include <stdio.h>
int sum(int x, int y);
void Result(int x, int y);
int main()
{
    int a= 0;
    int b= 0;
    int result=0;
    printf("a를 입력 : ");
    scanf("%d", &a);
    printf("b를 입력 : ");
    scanf("%d", &b);
    result=sum(a, b);
    printf("sum 함수 결과 : %d\n", result);
    printf("Result함수 결과 : ");
    Result(a,b);
    return 0;
}
int sum(int a, int b)
{
    int value;
    value = a+b;
    return value;
}
void Result(int a, int b)
{
    int value;
    value = a+b;
    printf("결과 : %d\n\n", value);
}