#include <stdio.h>

int main()
{
    int value=0;
    int is_prime=0;
    int count=0;

    int j=0;
    printf("2 이상의 정수를 입력하세요 : ");
    scanf("%d", &value);

    for(int i=2;i<=value;i++)
    {
        for(j=2;j<=i;j++)
        {
            
            if((i%j)==0)//여기서 걸러지는 숫자는 소수가 아님.
            {
                is_prime=1;
                break;
            }
            if(is_prime==0)
            {
                printf("%5d", i);
                is_prime=1;
                count++;
            }
            if(count>=5)
            {
                printf("\n");
                count=0;
            }
        }
        
        

        
    }




    return 0;
}