#include <stdio.h>

int main()
{
    int N=0;
    int X=0;
    int A[10000];

    printf("정수 N개로 이루어진 수열 A와 정수 X가 주어진다. 이때, A에서 X보다 작은 수를 모두 출력하는 프로그램을 작성하시오.\n");
    printf("1<=N, X<=10000\n");
    printf("수열의 갯수를 입력하시오 : ");
    scanf("%d", &N);
    printf("X의 값을 입력하시오 : ");
    scanf("%d", &X);

    for(int i=0; i<N;i++)
    {
        printf("A[%d] : ", i);
        scanf("%d", &A[i]);
        if(i==N-1)//배열 마지막에 공백을 넣어서 끝자리라고 지정해주기.
        {
            A[N]='\n';
        }
    }
    int count=0;
    for(int i=0;i<N;i++)
    {
        if(A[i]<X)
        {
            if(count==0)//맨처음 입력 때
            {
                printf("%d", A[i]);
            }
            else if(count%5==0)//맨 마지막 입력 때
            {
                printf("%d\n", A[i]);
            }
            else //평소 입력 떄
            {
                printf("%5d", A[i]);
            }
            count++;
        }
    }
    printf("\n");
    return 0;
}