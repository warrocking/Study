// /* Q15-1) 성적을 10개를 입력한다.
 

// 짝수번째 성적만 출력하세요.

// 단, 배열을 index값을 이용해 출력하세요.

// 0 1 2 3 4 5 6 7 8 9  - index 값

// 1 2 3 4 5 6 7 8 9 10 - 성적

// 짝수성적

// 2 4 6 8 10

// --------------------------------------------------------------------

// Q15-2) int arr[6] = {3, 7, 2, 9, 5, 1}

// 배열의 최대값과 index를 구하라.

// -------------------------------

// max : 9

// index : 3 */

#include <stdio.h>

int main()
{
    int arr[10];
    int max=0;
    int index;
    int arr_range = sizeof(arr) / sizeof(arr[0]);
    
    printf("총 10명의 점수를 입력하시오.\n");

    for(int i=0;i<arr_range;i++)
    {
        printf("%d.점수 입력 : ", i+1);
        scanf("%d", &arr[i]);
    }
    printf("\n\n");
    printf("짝수 출력 : ");
    for(int i=0;i<arr_range;i++)
    {
        if((arr[i]%2)==0)
        {
            printf("%5d", arr[i]);
        }
    }    
    printf("\n");

    printf("배열의 최대값과 index\n\n");

    for(int i=0;i<arr_range;i++)
    {
        if(arr[i] > max)
        {
            max = arr[i];
            index = i;
        }
    }
    printf("max : %d\n", max);
    printf("몇번째 값이 최대값인가 : index : %d\n", index+1);//index+1은 i=0부터 시작이니까.
    

    return 0;
}

// #define _CRT_SECURE_NO_WARNINGS
// #include <stdio.h>
// int main() {

// 	//Q15-1

// 	int score[10];

// 	for (int i = 0; i < 10; i++) {
// 		printf("%d번째 점수 입력 : ", i + 1);
// 		scanf("%d", &score[i]);
// 	}

// 	for (int i = 0; i < 10; i++) {
// 		if (i % 2 == 1) {
// 			printf("%d ", score[i]);
// 		}
// 	}

// 	//Q15-2

// 	int arr[6] = { 3,7,2,9,5,1 };
// 	int max = arr[0];
// 	int max_i = 0;

// 	for (int i = 0; i < 6; i++) {
// 		if (max < arr[i]) {
// 			max = arr[i];
// 			max_i = i;
// 		}

// 	}

// 	printf("\nmax : %d\nindex : %d", max, max_i);


// 	return 0;
// }