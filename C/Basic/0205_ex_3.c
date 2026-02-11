#include <stdio.h>

int main(){
    
    int temp =0;
    double celsius;//섭씨
    double fahrenheit;//화씨
    //화씨 온도 = 9/5*섭씨온도 +32
    //fahrenheit = 9/5*celsius +32

    //입력
    printf("자연수를 입력하세요 : ");
    scanf("%d", &temp);
    //수식
    celsius = (double)temp;
    fahrenheit = 9.0/5.0*celsius + 32.0;

    //출력
    printf("섭씨 온도 : %.2lf\n", celsius);
    printf("화씨 온도 : %.2lf\n", fahrenheit);
    
    
    return 0;

}