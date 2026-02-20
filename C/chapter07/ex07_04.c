#include <stdio.h>

void print_line(char ch, int count)
{
    int i;
    
    for(i=0;i<count;i++)
    {
        printf("%c", ch);
    }
    printf("\n");
}

int main()
{
    print_line('*', 50);
    printf("\t학번\t이름\t전공\t학점\n");
    print_line('*', 50);
    return 0;
}