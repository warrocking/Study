#include <stdio.h>

int main()
{
    char hellow[13];

    hellow[0] = 'H';
    hellow[1] = 'e';
    hellow[2] = 'l';
    hellow[3] = 'l';
    hellow[4] = 'o';
    hellow[5] = ' ';
    hellow[6] = 'w';
    hellow[7] = 'o';
    hellow[8] = 'r';
    hellow[9] = 'l';
    hellow[10] = 'd';
    hellow[11] = '!';
    hellow[12] = '\0';//문자, 문자열 구분에서는 매우 중요

    printf("%s\n", hellow);
    
    for(int i=0;i<13;i++)
    {
        printf("%c", hellow[i]);
    }
    printf("\n");


    return 0;
}