#include <stdio.h>
/* int main()
{
    int i;
    int index;
    int value;

    i = 0;
    while (i<100)
    {
        printf("i : %d\n", i);
        i++;
    }
    printf("i 최종값 : %d\n\n", i);

    index = 2;
    do
    {
        printf("index : %d\n", index);
        index = index * 2;
    }while(index<=100);
    printf("index 최종값 : %d\n\n", index);

    value = 100;
    for(; value>0; value-=5)
    {
        printf("value : %d\n", value);
    }
    printf("value 최종값 : %d\n\n", value);

    return 0;
} */

int main()
{
    int a = 1;
    while(a<10)
    {
        a*=2;
        printf("a : %d\n", a);
    }
    printf("최종 a 값 : %d\n", a);
    return 0;
}



