#include <stdio.h>
int get_num()
{
    int value;
    printf("값 입력 : ");
    scanf("%d", &value);
    return value;
}
int main()
{
    int result = get_num();
    printf("result : %d\n", result);

    return 0;
}