#include <stdio.h>

int main()
{
    char input[100];
    printf("문자열 입력 : ");
    scanf("%99s", input);
    
    
    // 첫글자만 문자인지 숫자인지 판별
    if((input[0] >= 'A' && input[0] <= 'Z') || (input[0] >= 'a' && input[0] <= 'z'))
    {
        printf("입력한 값은 문자입니다.\n");
    }
    else
    {
        printf("입력한 값은 문자가 아닙니다.\n");
    }
    
    return 0;
}
