#include <stdio.h>
/*
// 재귀식
 int factorial(int n)
{
    if (n <= 1)
    {
        return 1;
    }
    else
    {
        return n * factorial(n - 1);
    }
}

int main()
{
    int n = 10;
    printf("%d\n", factorial(n));
    return 0;
}


*/

// 점화식

int main()
{
    int n = 5;
    int dp[10];

    dp[0] = 1;

    for (int i = 1; i <= n; i++)
    {
        dp[i] = i * dp[i - 1];
        printf("dp[%d] = %d\n", i, dp[i]);
    }

    return 0;
}
