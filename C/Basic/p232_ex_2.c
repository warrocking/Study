#include <stdio.h>


void sum(int x)
{
    int value=0;
    for(int i=0;i<=x;i++)
    {
        value+=i;
    }
    printf("1부터 %d까지의 합은 %d입니다.\n", x, value);

}

int main()
{
    sum(10);
    sum(100);
    return 0;
}
