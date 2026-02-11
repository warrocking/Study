#include <stdio.h>

void print_char(char ch, int count)
{
    int i;
    for(i=0;i<count;i++)
    {
        printf("%c", ch);
    }
    printf("\n");
    return ;
}

int main()
{
    char input;
    printf("단일 문자 입력 : ");
    scanf("%c", &input);
    print_char(input, 5);
    return 0;
}