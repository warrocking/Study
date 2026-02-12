// 문제 요약:
#include <stdio.h>
// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언
void input_ary(double *pa, int size)
{
    printf("%d개의 실수값 입력 : ", size);
    for (int i = 0; i < size; i++)
    {
        scanf("%lf", pa + i);
    }
}

double find_max(double *pa, int size)
{
    double max;

    max = pa[0];

    for (int i = 0; i < size; i++)
    {
        if (pa[i] > max)
        {
            max = pa[i];
        }
    }
    return max;
}

int main(void)
{
    // 선언
    double ary[5];
    double max;
    int size;

    // 입력
    size = sizeof(ary) / sizeof(ary[0]);

    // 처리
    input_ary(ary, size);
    max = find_max(ary, size);

    // 출력
    printf("배열의 최댓값 : %.3f\n", max);

    // 함수 종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/