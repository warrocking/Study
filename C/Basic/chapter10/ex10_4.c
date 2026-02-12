// 문제 요약: 포인터의 뺄셈과 관계 연산
#include <stdio.h>
// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 선언
    int ary[5] = {10, 20, 30, 40, 50};
    int *pa = ary;
    int *pb = pa + 3;

    // 입력
    printf("pa : %p\n", pa);
    printf("pb : %p\n", pb);
    printf("pa : %d\n", pa);
    printf("pb : %d\n", pb);

    // 처리
    pa++;

    // 출력
    printf("pb - pa : %u\n", pb - pa);
    printf("앞에 있는 배열 요소의 값 출력 : ");
    if (pa < pb)
    {
        printf("%d\n", *pa);
    }
    else
    {
        printf("%d\n", *pb);
    }

    // 함수 종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/