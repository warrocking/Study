#include <stdio.h>

int main(){
    short sh = 32768;
    int in = 2147483648;
    long ln = 2147483648;
    long long lnln = 9223372036854775808;

    
    printf("short형 변수 최대값 : %d\n", sh-1);
    printf("int형 변수 최대값 : %d\n", in-1);
    printf("long형 변수 최대값 : %ld\n", ln-1);
    printf("long long형 변수 최대값 : %lld\n", lnln-1);

    printf("\n");

    printf("short형 변수 최소값 : %d\n", sh);
    printf("int형 변수 최소값 : %d\n", in);
    printf("long형 변수 최소값 : %ld\n", ln);
    printf("long long형 변수 최소값 : %lld\n", lnln);

    printf("\n");

    printf("short형 변수 unsigned값 : %u\n", sh);
    printf("int형 변수 unsigned값 : %u\n", in);
    printf("long형 변수 unsigned값 : %lu\n", ln);
    printf("long long형 변수 unsigned값 : %llu\n", lnln);

    return 0;
    
}