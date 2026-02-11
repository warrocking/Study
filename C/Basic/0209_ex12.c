#include <stdio.h>

int main()
{
    int star;
    
    
    printf("1~20 사이의 정수를 입력하세요. : ");
    scanf("%d", &star);

/*     for(int i=0;i<star;i++)
    {
        for(int j=0;j<=i;j++)
        {
            printf("*");
        }
        printf("\n");
    }
    
    printf("\n\n거꾸로\n\n"); */
    /* printf("\n");
    for(int i=0;i<star;i++)
    {
        for(int j=star-i;j>0;j--)
        {
            printf("0");
        }
        for(int j=0;j<i-1;j++)
        {
            printf("*");
        }
        for(int j=i;j>0;j--)
        {
            printf("*");
        }
        for(int j=0;j<star-i;j++)
        {
            printf("0");
        }
        printf("\n");
    }
    for(int i=star;i>0;i--)
    {
        for(int j=star-i;j>0;j--)
        {
            printf("0");
        }
        for(int j=0;j<i;j++)
        {
            printf("*");
        }
        for(int j=i;j>0;j--)
        {
            printf("*");
        }
        for(int j=0;j<star-i;j++)
        {
            printf("0");
        }
        printf("\n");
    } */
    /* printf("\n\n거꾸로\n\n");
    printf("\n\n거꾸로\n\n");
    for(int i=0;i<star;i++)
    {
        for(int j=0;j<star-i;j++)
        {
            printf("*");
        }
        printf("\n");
    } */
/*     int half= star/2;
    for(int i=0;i<star/2+1; i++)
    {
        for(int j=star/2;j>i;j--)
        {
            printf("0");
        }
        for(int k=0;k<i;k++)
        {
            if(k==star/2+1)
            {
                printf("0");
            }
            else
            {
                printf("*");
            }
        }
        
        for(int j=star/2;j>i;j--)
        {
            printf("0");
        }
        printf("\n");

    } */

    /* printf("\n");

    for (int i = 0; i < star; i++)
    {
        for (int j = 0; j < star - 1 - i; j++)
        {
            printf("0");
        }
        for (int j = 0; j < 2 * i + 1; j++)
        {
            printf("*");
        }
        for (int j = 0; j < star - 1 - i; j++)
        {
            printf("0");
        }
        printf("\n");
    }
    //
    for (int i = star - 2; i >= 0; i--)
    {
        for (int j = 0; j < star - 1 - i; j++)
        {
            printf("0");
        }
        for (int j = 0; j < 2 * i + 1; j++)
        {
            printf("*");
        }for (int j = 0; j < star - 1 - i; j++)
        {
            printf("0");
        }
        printf("\n");
    } */
    int n;
    if (scanf("%d", &n) != 1 || n < 1) return 0;
    for (int i = 0; i < 2 * n - 1; i++)
    {
        //마름모에서 현재 층의 높이
        int row = (i < n) ? i : (2 * n - 2 - i);
        /* if(i<n)
        {
            row = i;
        }
        else
        {
            row = 2*n-2-i;
        } */



        //왼쪽 정렬을 위한 공백 수
        int spaces = n - 1 - row;
        //별의 갯수
        int stars = 2 * row + 1;//홀수 갯수

        for (int j = 0; j < spaces; j++) 
            putchar('0');
        for (int j = 0; j < stars; j++) 
            putchar('*');
        putchar('\n');
    }


    return 0;
}