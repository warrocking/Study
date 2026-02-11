#include <stdio.h>

int main()
{
    int score[5];
    int i;
    int total=0;
    float avg;
    int count;

    count = sizeof(score) / sizeof(score[0]);
    for(int i=0;i<count;i++)
    {
        printf("점수 입력 : ");
        scanf("%d", &score[i]);
        total += score[i];
        printf("score[%d] : %d\n\n", i,score[i]);
    }
    
    avg = total / (double)count;
    
    printf("\n");
    printf("평균 : %.2f\n", avg);






    return 0;
}