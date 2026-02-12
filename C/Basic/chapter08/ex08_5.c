#include <stdio.h>

int main()
{
    char str1[80] = "cat";
    char str2[80];
    char str3[80]= "Lion";
    strcpy(str1, "triger");
    printf("str1 : %s, str2 : %s, str3 : %s\n", str1, str2, str3);

    strcpy(str2, str1);
    printf("str1 : %s, str2 : %s, str3 : %s\n", str1, str2, str3);

    strcpy(str3, str1);
    printf("str1 : %s, str2 : %s, str3 : %s\n", str1, str2, str3);


    return 0;
}