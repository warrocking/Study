#include <stdio.h>
// #include <string.h>

int main()
{

    char fruit[11] = "strawberry";
    char fruit_watermelon[] = "watermelon";

    printf("딸기 : %s\n", fruit);
    printf("딸기 잼 : %sJam\n", fruit);

    printf("수박 : %s\n", fruit_watermelon);

    strcpy(fruit, "banana");
    printf("바나나 : %s\n", fruit);

    return 0;
}