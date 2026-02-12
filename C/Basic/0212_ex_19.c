/* #include <stdio.h>
int sum(int x, int y)
{
    return x + y;
}
int diff(int x, int y)
{
    if (x > y)
    {
        return x - y;
    }
    else
    {
        return y - x;
    }
}
int mul(int x, int y)
{
    return x * y;
}
int div(int x, int y)
{
    if (x > y)
    {
        return x / y;
    }
    else
    {
        return y / x;
    }
}

int main()
{
    int inputValue1, inputValue2;
    int inputSize = 0;
    int result[4];

    printf("2개의 정수를 각각 입력해주세요.\n");
    printf("입력 1 : ");
    scanf("%d", &inputValue1);
    printf("입력 2 : ");
    scanf("%d", &inputValue2);

    result[0] = sum(inputValue1, inputValue2);
    result[1] = diff(inputValue1, inputValue2);
    result[2] = mul(inputValue1, inputValue2);
    result[3] = div(inputValue1, inputValue2);

    printf("사칙연산 결과(합, 차, 곱, 나누기 순)\n");
    // 결과 출력
    for (int i = 0; i < sizeof(result) / sizeof(result[0]); i++)
    {
        printf("result[%d] : %d\t", i + 1, result[i]);
    }

    return 0;
}
 */
#include <stdio.h>
int sum(int x, int y)
{
    return x + y;
}
int diff(int x, int y)
{
    return (x > y) ? (x - y) : (y - x);
}
int mul(int x, int y)
{
    return x * y;
}
int div(int x, int y)
{
    return (x > y) ? (x / y) : (y / x);
}

int main()
{
    int inputValue1, inputValue2;
    int inputSize = 0;

    printf("2개의 정수를 각각 입력해주세요.\n");
    printf("입력 1 : ");
    scanf("%d", &inputValue1);
    printf("입력 2 : ");
    scanf("%d", &inputValue2);

    int result[4] = {
        sum(inputValue1, inputValue2),
        diff(inputValue1, inputValue2),
        mul(inputValue1, inputValue2),
        div(inputValue1, inputValue2)};

    // 결과 출력
    printf("사칙연산 결과(합, 차, 곱, 나누기 순)\n");
    for (int i = 0; i < sizeof(result) / sizeof(result[0]); i++)
        printf("result[%d] : %d\n", i + 1, result[i]);

    return 0;
}
