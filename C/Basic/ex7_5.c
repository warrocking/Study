/* #include <stdio.h>
#include <string.h>

void fruit(int count, char *fruit_name)
{
    for(int i=0;i<count;i++)
    {
        for(int j=0;j<strlen(fruit_name);j++)
        {
            printf("%c", fruit_name[j]);
        }
        printf("\n");
    }
    
}

int main()
{
    int count;
    char fruit_name[100];
    printf("과일 이름 입력 : ");
    scanf("%s", fruit_name);
    printf("반복 횟수 : ");
    scanf("%d", &count);
    fruit(count, fruit_name);
    return 0;
} */

#include <stdio.h>
void fruit(int count);
int main()
{
    fruit(1);
    return 0;

}
void fruit(int count)
{
    
    printf("%d : apple\n", count);

    if(count==1000)
        return ;
    fruit(count+1);
}

