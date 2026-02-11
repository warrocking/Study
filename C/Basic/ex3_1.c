#include <stdio.h>

int main (){
    char ch = 'A';
    double da = 3.5;
    int a;//초기화 안하면 0 이나 에러.
    printf("%.2lf\n", da);
    printf("%c\n", ch);
    printf("%d\n", a);
    return 0;

}