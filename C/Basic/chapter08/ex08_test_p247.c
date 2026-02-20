#include <stdio.h>

int main()
{
    int A[3]={1, 2, 3};
    int B[10];
    for(int i=0;i<(sizeof(B)/sizeof(B[0]));i++)
    {
        B[i]=A[i%3];
        printf("B[%d] : A[%d] = %d\n\n", i, i, B[i]);
    }
    return 0;
}