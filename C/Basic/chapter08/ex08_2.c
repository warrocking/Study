#include <stdio.h>

int main()
{
/*     int a, b, c, d, e;
    int arr[5];

    for(int i=0;i<5;i++)
    {
        arr[i]= i+10;
    }

    for(int i=0;i<5;i++)
    {
        printf("%d\n", arr[i]);
    }
    printf("\n"); */

    /* int score[5];
    int i;
    int total = 0;
    float avg;

    for(i=0;i<5;i++){
        printf("입력 : ");
        scanf("%d", &score[i]);
    
    }
    for(i=0;i<5;i++)
    {
        total += score[i];
    }
    avg = total / 5.0;

    for(i=0;i<5;i++)
    {
        printf("%5d", score[i]);
    }
    printf("\n");
    
    printf("평균 : %.2f\n", avg); */


    int score[3];
    int total=0;
    float avg;
    printf("국영수 순서로 입력 : ");
    for(int i=0;i<3;i++)
    {
        scanf("%d", &score[i]);
    }
    printf("국어 : %d\n", score[0]);
    printf("영어 : %d\n", score[1]);
    printf("수학 : %d\n", score[2]);
    for(int i=0;i<3;i++)
    {
        total += score[i];
    }
    avg = total / 3.0;
    printf("총점 : %d\n", total);
    printf("평균 : %.2f\n", avg);


    return 0;
}