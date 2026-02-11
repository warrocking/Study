#include <stdio.h>

int main() {
    int value1, value2;
    int value_null = 0;

    printf("값 입력 1번 : ");
    scanf("%d", &value1);
    printf("값 입력 2번 : ");
    scanf("%d", &value2);
    
    printf("1번 : %d / 2번 : %d\n", value1, value2);

    printf("값 위치 바꾸기 실행\n");
    value_null = value1;
    value1 = value2;
    value2 = value_null;

    printf("1번 : %d / 2번 : %d\n", value1, value2);

    return 0;
}