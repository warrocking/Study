#include <stdio.h>

int main()
{
    int tribe;//종족 입력 변수
    
    
    printf("종족을 입력하세요\n1. 외계인\n2. 사람\n3. 군인\n입력값: ");
    scanf("%d", &tribe);

    printf("\n<if-else문으로 출력>\n\n");

    if(tribe == 1) //외계인
    {
        printf("나는 외계인을 보았습니다. \n");
    }
    else if(tribe == 2) //사람
    {
        printf("나는 사람을 보았습니다.\n");
    }
    else if(tribe == 3) //군인
    {
        printf("나는 군인을 보았습니다. \n");
    }
    else //잘못된 입력
    {
        printf("잘못된 입력입니다.\n");
    }



    printf("\n<switch문으로 변경>\n\n");
    switch (tribe)
    {
    case 1:
        printf("나는 외계인을 보았습니다. \n");
        break;
    case 2:
        printf("나는 사람을 보았습니다.\n");
        break;
    case 3:
        printf("나는 군인을 보았습니다. \n");
    default:
        printf("잘못된 입력입니다.\n");
        break;
    }


    return 0;
}