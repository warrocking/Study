// 문제 내용 작성
/*


*/
#include <stdio.h>

int main(void)
{
    // 변수 지정 ;
    int a = 10, b = 20;
    const int *pa = &a;
    const double pi = 3.141592;

    // 함수 작성
    pa = &b;
    pa = &a;

    // 결과 출력
    printf("pa = %u\n", &pa);

    // 메인 함수 종료
    return 0;
}
