#include <stdio.h>

int main()
{
    int star=0;

    printf("정수를 입력하시오 : ");
    scanf("%d", &star);

    printf("\n문제 1\n\n");
    for(int i=0;i<=star;i++)
    {
        for(int j=0;j<i;j++)
        {
            printf("*");
        }
        printf("\n");
    }

    printf("\n문제 2\n\n");
    for(int i=0;i<star;i++)
    {
        for(int j=star;j>i;j--)
        {
            printf("*");
        }
        printf("\n");
    }

    printf("\n문제 3\n");//5기준
    for(int i=0;i<star;i++)
    {
        for(int j=star;j>i+1;j--)
        {
            printf(" ");
        }
        for(int k=0;k<i*2+1;k++)
        {
            printf("*");
        }
        printf("\n");
    }
    

    printf("\n문제 4\n");
    for(int i=0;i<star;i++)
    {
        for(int j=0;j<i;j++)
        {
            printf(" ");
        }
        for(int k=2*star-i;k>i+1;k--)
        {
            printf("*");
        }
        printf("\n");
    }




    printf("\n문제 5\n\n");

    for(int i=0;i<star;i++)
    {
        for(int j=0;j<star-i-1;j++)
        {
            printf(" ");
        }
        for(int k=0;k<i*2+1;k++)
        {
            printf("*");
        }
        printf("\n");
    }
    for(int i=star-2;i>=0;i--)
    {
        for(int j=0;j<star-i-1;j++)
        {
            printf(" ");
        }
        for(int k=0;k<i*2+1;k++)
        {
            printf("*");
        }
        printf("\n");
    }
    return 0;
}