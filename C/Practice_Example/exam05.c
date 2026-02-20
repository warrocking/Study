#include <stdio.h>

int main()
{
    int arr[5] = {2, 4, 6, 8, 10};
    for (int i = (int)(sizeof(arr) / sizeof(arr[0])) - 1; i >= 0; i--)
    {
        if (arr[i] % 2 == 0)
            printf("%d\n", arr[i]);
    }

    /* for(int i=0;i<5;i++)
    {
        arr[i]= 10-(i*2);
        printf("%d\n", arr[i]);
    } */

    return 0;
}