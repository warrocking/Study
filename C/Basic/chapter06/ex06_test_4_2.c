// 표준 입출력 함수(printf, scanf)를 사용하기 위한 헤더
#include <stdio.h>

int main(void)
{
    // 사용자로부터 입력받을 정수
    int n;
    // 2 이상의 정수를 입력받는다
    printf("2 이상의 정수를 입력하세요 : ");
    // 입력이 정상인지 확인하고, 2 미만이면 종료
    if (scanf("%d", &n) != 1 || n < 2) 
    {
        printf("잘못된 입력입니다. 프로그램을 종료합니다.\n");
        return 0;
    }

    // 출력한 소수의 개수(5개마다 줄바꿈을 위해 사용)
    int count = 0;

    // 2부터 n까지 모든 수를 하나씩 검사
    for (int i = 2; i <= n; i++) {
        // 일단 i를 소수라고 가정
        int is_prime = 1;
        // 2부터 i-1까지 나눠서 하나라도 나눠떨어지면 소수가 아니다
        for (int j = 2; j < i; j++) {
            if (i % j == 0) {
                // 나누어 떨어지면 소수가 아니므로 표시하고 반복 종료
                is_prime = 0;
                break;
            }
        }
        // 소수로 판정되면 출력
        if (is_prime) {
            // 5칸 폭으로 출력하여 간격 맞추기
            //printf("%5d", i); 
            printf("\t%d\t", i);
            // 출력 개수 증가
            count++;
            // 5개 출력했으면 줄바꿈
            if (count % 5 == 0) {
                printf("\n");
            }
        }
    }

    // 마지막 줄이 5개로 딱 맞지 않으면 줄바꿈 한 번 추가
    if (count % 5 != 0) 
    {
        printf("\n");
    }

    // 정상 종료
    return 0;
}
