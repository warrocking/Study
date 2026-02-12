// 문제 요약:
#include <stdio.h>
// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 선언
    int ary[3];
    int *pa = ary;
    int i;

    // 입력
    *pa = 10;
    *(pa + 1) = 20;

    // 처리
    pa[2] = pa[0] + pa[1];

    // 출력
    for (int i = 0; i < 3; i++)
    {
        printf("pa[%d]=%d\n", i, pa[i]);
    }

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/