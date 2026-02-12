// 문제 요약:
#include <stdio.h>
// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언
void print_ary(int *pa)
{
    for (int i = 0; i < 5; i++)
    {
        printf("%d\n", pa[i]);
    }
}

int main(void)
{
    // 선언
    int ary[5] = {10, 20, 30, 40, 50};

    // 입력

    // 처리
    print_ary(ary);

    // 출력

    // 함수 종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/