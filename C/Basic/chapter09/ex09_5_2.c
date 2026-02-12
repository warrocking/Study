// 문제 요약: 주소와 포인터의 크기
#include <stdio.h>

int main(void)
{
    // 선언
    char ch;
    int in;
    double db;

    char *pc = &ch;
    int *pi = &in;
    double *pd = &db;
    // 입력

    // 처리
    printf("sizeof(&ch) : %d\n", sizeof(&ch));
    printf("sizeof(&int) : %d\n", sizeof(&in));
    printf("sizeof(&db) : %d\n", sizeof(&db));

    printf("\n");

    printf("sizeof(pc) : %d\n", sizeof(pc));
    printf("sizeof(pi) : %d\n", sizeof(pi));
    printf("sizeof(pd) : %d\n", sizeof(pd));

    printf("\n");

    printf("sizeof(ch) : %d\n", sizeof(ch));
    printf("sizeof(int) : %d\n", sizeof(in));
    printf("sizeof(db) : %d\n", sizeof(db));

    printf("\n");

    // 출력

    return 0;
}