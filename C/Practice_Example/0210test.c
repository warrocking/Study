#include <stdio.h>
void fun1();
void fun2();
void fun3();

void fun1()
{
    printf("연결 1\n");
    fun2();
}

void fun2()
{
    printf("연결 2\n");
    fun3();
}

void fun3()
{
    printf("연결 3\n");
}

int main()
{
    fun1();
    return 0;
}