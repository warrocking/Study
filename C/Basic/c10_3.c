// 문제 요약:
#include <stdio.h>
// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 선언
    int ary[3] = {10, 20, 30};
    int *pa = ary;

    // 입력

    // 처리

    // 출력
    printf("배열의 값 : ");
    for (int i = 0; i < 3; i++)
    {
        printf("%d ", *pa);
        pa++;
    }

    // 함수 종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/