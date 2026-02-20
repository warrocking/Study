/*
나이(age)에 따라 입장료를 출력하는 프로그램입니다. 아래 조건에 맞게 else if 문을 사용하여 코드를 설계해 보세요.

65세 이상: "무료"

13세 이상 64세 이하: "10,000원"

12세 이하: “5,000원”

*/
/*
#include <stdio.h>

int main(){
    int age;
    printf("나이 : ");
    scanf("%d", &age);

    if(age >= 65)
    {
        printf("무료입니다.\n");
    }
    else if(age >= 13 && age <= 64)
    {
        printf("입장료는 10,000원입니다.\n");
    }
    else // 12세 이하
    {
        printf("입장료는 5,000원입니다.\n");
    }
    
    return 0;
}
*/
/*
 개인 파생 문제 : 가족 인원 수를 입력하고 각 인원에 따른 총 가격을 구하시오.
 조건은 위와 같음.
*/
#include <stdio.h>

int main(){

    int age;
    int count;
    int total_price =0;

    //13세 이하 체크
    printf("13세 이하 혹은 65세 이상은 몇명인가요? : ");
    scanf("%d", &count);
    total_price += count * 0; // 7세 이하 무료
    count = 0;// 초기화
    
    // 13세 부터 65세 체크
    printf("13세 이상 65세 이하는 몇명인가요? : ");
    scanf("%d", &count);
    total_price += count * 10000; // 13세 이상 65세 이하는 10,000원
    count = 0;// 초기화

    /*
    // 65세 이상 체크
    printf("65세 이상은 몇명인가요? : ");
    scanf("%d", &count);
    total_price += count * 0; // 65세 이상 무료
    count = 0;// 초기화
    */

    printf("총 입장료는 %d원 입니다.\n", total_price);
    return 0;
}

