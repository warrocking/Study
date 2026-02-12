#include <stdio.h>

void printf_max(int array[], int sizeof_array)
{
    int max = 0;
    int count = sizeof_array;
    for (int i = 0; i < count; i++)
    {
        if (max <= array[i])
        {
            max = array[i];
        }
    }
    printf("max : %d\n", max);
    return;
}
int main()
{

    int array[7] = {4, 5, 8, 1, 2, 10, 7};
    printf_max(array, sizeof(array) / sizeof(array[0]));

    return 0;
}