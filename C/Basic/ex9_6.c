// 문제 요약: 허용되지 않는 포인터의 대입
#include <stdio.h>

int main(void)
{
    // 선언
    double a = 3.4;
    double *pd = &a;
    int *pi;

    // 입력

    // 처리
    pi = (int *)pd;

    // 출력
    printf("%.2lf\n", *pd);

    return 0;
}