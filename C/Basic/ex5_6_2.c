#include <stdio.h>

int main()
{
    int n;
    printf("정수 입력 : ");
    scanf("%d", &n);
    switch ((n%3))
    {
    case 0:
        printf("거짓\n");
        break;
    
    case 1:
    case 2:
    default:
        printf("참\n");
        break;
    // default:
    //     printf("에러\n");
    //     break;
    }
}