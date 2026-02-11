#include <stdio.h>

int main()
{
    int a= 20, b=10;
    // if(a>10)
    // {
    //     if(b>=0)
    //         b=1;
    //     else
    //         b=-1;
    // }

    b = (a>10) ? ((b>=0) ? 1 : -1) : b;

    printf("a : %d, b : %d\n", a, b);
    return 0;
}