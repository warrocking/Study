// 문제 요약:
#include <stdio.h>
// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 선언
    int ary[3];

    // 입력
    *(ary + 0) = 10;
    *(ary + 1) = *(ary + 0) + 10;

    printf("세 번쨰 배열 요소에 키보드 입력 : ");
    scanf("%d", ary + 2);

    // 처리
    for (int i = 0; i < 3; i++)
    {
        printf("*ary[%d] = %d\n", i, *(ary + i));
    }
    for (int i = 0; i < 3; i++)
    {
        printf("ary[%d] = %d\n", i, ary[i]);
    }
    // 출력

    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/