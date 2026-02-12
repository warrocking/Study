// 문제 요약: 포인터 없이 두 변수 값을 바꾸는 함수 - 변수의 값을 인수로 주는 경우
#include <stdio.h>

// 함수 선언
void swap(int *x, int *y)
{
    int temp;
    temp = *x;
    *x = *y;
    *y = temp;
}
/* void swap(int x, int y)
{
    int temp;
    temp = x;
    x = y;
    y = temp;
    printf("swap -> a : %d, b:%d\n", x, y);
} */
int main(void)
{
    // 선언
    int a = 10, b = 20;

    // 입력

    // 처리
    swap(&a, &b);
    // swap(a, b);

    // 출력
    printf("a : %d, b:%d\n", a, b);

    return 0;
}
