#include <stdio.h>
#define _CRT_SECURE_NO_WARNINGS

int main() {
    int width;
    int height;
    int area;
    printf("삼각형의 넓이를 구합니다.\n");
    printf("가로 길이 : ");
    scanf("%d", &width);
    printf("세로 길이 : ");
    scanf("%d", &height);
    area = width * height / 2;
    printf("\n삼각형의 넓이(area) : %d\n", area);

    return 0;

}