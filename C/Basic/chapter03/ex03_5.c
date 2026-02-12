#include <stdio.h>

int main(){
    float ft = 1.234567890123456789;
    double db = 1.234567890123456789;
    long double ldb = 1.234567890123456789;

    printf("float형 변수 : %.20f\n", ft);
    printf("double형 변수 : %.20f\n", db);
    printf("long double형 변수 : %.20Lf\n", ldb);

    
    return 0;

}