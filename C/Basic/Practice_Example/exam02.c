#include <stdio.h>

int main() {
    int year;
    int age;
    printf("연도를 입력하세요: ");
    scanf("%d", &year);
    age = 2026 - year;
    printf("나이 : %d\n", age);
    
    return 0;

}