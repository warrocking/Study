/* #include <stdio.h>
#include <string.h>
int main()
{
    int scoreInput[3];
    char nameInput[3][10];
    int i;
    int scoreOutput[3];
    char nameRate[3][10];
    for(i=0; i<3; i++)
    {
        printf("이름 입력 : ");
        scanf("%s", nameInput[i]);
        printf("점수 입력 : ");
        scanf("%d", &scoreInput[i]);
        printf("\n");
    }
    for(i=0; i<3; i++)
    {
        printf("이름 : %s, 점수 : %d\n", nameInput[i], scoreInput[i]);
    }
    
    if(scoreInput[0]>=scoreInput[1] && scoreInput[0]>=scoreInput[2])
    {
        scoreOutput[0] = scoreInput[0];
        strcpy(nameRate[0], nameInput[0]);

    }
    else if(scoreInput[1]>=scoreInput[0] && scoreInput[1]>=scoreInput[2])
    {
        scoreOutput[0] = scoreInput[1];
        strcpy(nameRate[0], nameInput[1]);
    }
    else
    {
        scoreOutput[0] = scoreInput[2];
        strcpy(nameRate[0], nameInput[2]);
    }
    
    

    printf("\n\n1등 점수는 %s의 %d점입니다.\n", nameRate[0], scoreOutput[0]);

    return 0;
} */

/* int main()
{
    int score1;
    int score2;
    int score3;
    
    printf("철수 점수 : ");
    scanf("%d", &score1);
    printf("영희 점수 : "); 
    scanf("%d", &score2);
    printf("민수 점수 : "); 
    scanf("%d", &score3);

    if(score1 >= score2 && score1 >= score3)
    {
        if(score1 == score2 && score1 == score3)
        {
            printf("3명 모두 동점입니다. 점수 : %d\n", score1);
            return 0;
        }
        else if(score1 == score2)
        {
            printf("철수와 영희가 공동 1등입니다. 점수 : %d\n", score1);
            return 0;
        }
        else if(score1 == score3)
        {
            printf("철수와 민수가 공동 1등입니다. 점수 : %d\n", score1);
            return 0;
        }
        printf("1등은 철수입니다. 점수 : %d\n", score1);
    }
    else if(score2 >= score1 && score2 >= score3)
    {
        printf("1등은 영희입니다. 점수 : %d\n", score2);
    }
    else
    {
        printf("1등은 민수입니다. 점수 : %d\n", score3);
    }
    return 0;
} */


/* #include <stdio.h>

int main(void)
{
    int score[3];
    char name[3][10];

    for (int i = 0; i < 3; i++)
    {
        printf("이름 입력 : ");
        scanf("%9s", name[i]);
        printf("점수 입력 : ");
        scanf("%d", &score[i]);
        printf("\n");
    }

    for (int i = 0; i < 3; i++)
    {
        printf("이름 : %s, 점수 : %d\n", name[i], score[i]);
    }

    int max_score = score[0];
    for (int i = 1; i < 3; i++)
    {
        if (score[i] > max_score)
        {
            max_score = score[i];
        }
    }

    int top_count = 0;
    for (int i = 0; i < 3; i++)
    {
        if (score[i] == max_score)
        {
            top_count++;
        }
    }

    printf("\n\n1등 점수는 %d점입니다.\n", max_score);
    if (top_count == 1)
    {
        for (int i = 0; i < 3; i++)
        {
            if (score[i] == max_score)
            {
                printf("단독 1등: %s\n", name[i]);
                break;
            }
        }
    }
    else
    {
        printf("공동 1등: ");
        for (int i = 0; i < 3; i++)
        {
            if (score[i] == max_score)
            {
                printf("%s ", name[i]);
            }
        }
        printf("\n");
    }

    return 0;
}

 */


#include <stdio.h>

int main(void)
{
    int score[3];
    char name[3][10];

    for (int i = 0; i < 3; i++)
    {
        printf("이름 입력 : ");
        scanf("%9s", name[i]);
        printf("점수 입력 : ");
        scanf("%d", &score[i]);
        printf("\n");
    }

    for (int i = 0; i < 3; i++)
    {
        printf("이름 : %s, 점수 : %d\n", name[i], score[i]);
    }

    int max_score = score[0];
    for (int i = 1; i < 3; i++)
    {
        if (score[i] > max_score)
        {
            max_score = score[i];
        }
    }

    int top_count = 0;
    for (int i = 0; i < 3; i++)
    {
        if (score[i] == max_score)
        {
            top_count++;
        }
    }

    printf("\n\n1등 점수는 %d점입니다.\n", max_score);
    if (top_count == 1)
    {
        for (int i = 0; i < 3; i++)
        {
            if (score[i] == max_score)
            {
                printf("1등: %s\n", name[i]);
                break;
            }
        }
    }
    else
    {
        printf("공동 1등: ");
        for (int i = 0; i < 3; i++)
        {
            if (score[i] == max_score)
            {
                printf("%s ", name[i]);
            }
        }
        printf("\n");
    }

    return 0;
}







