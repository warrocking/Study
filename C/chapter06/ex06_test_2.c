#include <stdio.h>

int main()
{
    int count = 0;
    for(int i=0;i<3;i++)
    {
        for(int j=0;j<4;j++)
        {
            printf("Be happy\n");
            count++;
            if(j==2)
            {
                printf("중간에 탈출\n");
                break;
            }
        }
    }
    printf("총 출력 횟수: %d\n", count);
    return 0;
}