#include <stdio.h>
int main()
{
    char id[50];
    scanf("%49s", id);
    for (int i = 0; i < sizeof(id) / sizeof(id[0]); i++)
    {
        if (65 < id[i] && id[i] < 90)
        {
            id[i] = id[i] + 32;
        }
    }
    printf("%s??!\n", id);
    return 0;
}