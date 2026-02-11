#include <stdio.h>

int main() 
{
    char grade;
    char name[20];
    // array , name[0], name[1], ....., name[N-1]
    // name -> 포인터 변수 name[0]의 시작 주소
    printf("학점 : ");
    scanf("%c", &grade);

    printf("이름 : ");
    scanf("%s", name);//name은 주소이기 때문에 주소연산자를 사용하지 않음.


    return 0;
}