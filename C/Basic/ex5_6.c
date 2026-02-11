#include <stdio.h>
int main()
{
    //변수 지정
    int rank;
    int money;

    // 입력
    printf("랭크를 입력하시오(1~3) : ");
    scanf("%d", &rank);
    
    // 변수 구분
    // switch (rank)
    // {
    //     case 1:
    //         money = 300;
    //         break;
    //     case 2:
    //         money = 200;
    //         break;
    //     case 3:
    //         money = 100;
    //         break;
    //     default:
    //         money = 50;
    //         break;
    // }
    // if(rank ==1)
    // {
    //     money = 300;
    // }
    // else if(rank ==2)
    // {
    //     money = 200;
    // }
    // else if(rank ==3)
    // {
    //     money = 100;
    // }
    // else
    // {
    //     money = 50;
    // }

    
    money = Rank(rank);

    //출력
    printf("랭크에 따른 배당금 : %d만원\n", money);
    return 0;
}
int Rank(int rank)
{
    int money;
    switch (rank)
    {
        case 1:
            money = 300;
            break;
        case 2:
            money = 200;
            break;
        case 3:
            money = 100;
            break;
        default:
            money = 50;
            break;
    }
    return money;
}