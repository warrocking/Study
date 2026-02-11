#include <stdio.h>

int main()
{
    int ary[5];
    ary[0] = 10;
    ary[1] = 20;
    ary[2] = ary[0]+ary[1];
    printf("입력 : ");
    scanf("%d", &ary[3]);
    printf("%d\n", ary[0]);
    printf("%d\n", ary[1]);
    printf("%d\n", ary[2]);
    printf("%d\n", ary[3]);
    printf("%d\n", ary[4]);

    return 0;

}