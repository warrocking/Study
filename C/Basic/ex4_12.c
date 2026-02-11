#include <stdio.h>

int main()
{
    int a , b, res;

    printf("a : ");
    scanf("%d", &a);
    printf("b : ");
    scanf("%d", &b);
    
    if(a > b)
    {
        res = a;
    }
    else
    {
        res = b;
    }
    printf("res : %d\n", res);

    // 압축형
    //res = (a > b) ? a : b; 

    return 0;
}