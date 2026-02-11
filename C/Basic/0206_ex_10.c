#include <stdio.h>

int main()
{   
    int x;
    int y;
    
    int dan;
    printf("원하는 구구단 수 : ");
    scanf("%d", &dan);


    for(x=1;x<10;x++)
    {
        printf("%d x %d = %d\n", dan, x, x*dan);
    }  
    printf("\n\n"); 

    printf("for문\t\n\n");

    for(y=1;y<=10;y++)
    {
        for(x=1;x<10;x++)
        {
            printf("%d x %d = %d\n", y, x, x*y);
        }  
        printf("\n\n"); 
    }
    //------------------------
    /* y=9;
    x=9; */
    printf("\n\n 구구단 거꾸로 출력해보기 \n\n");
    for(y=9;y>0;y--)
    {
        for(x=9;x>0;x--)
        {
            printf("%d x %d = %d\n", y, x, x*y);
        }
        printf("\n");
    }


    printf("while문으로 변경\t\n\n");
    
    



    x=1, y=1;
    while(y<=10)
    {
        x=1;//매번 초기화를 해줘야 1부터 9까지의 구구단이 됨.
        while(x<=10)
        {
            printf("%d x %d = %d\n", y, x, x*y);
            x++;
        }
        y++;
        printf("\n\n");
    }
    return 0;
}