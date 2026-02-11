// #include <stdio.h>


// int main(){
    
//     //값을 받을 변수 지정
//     int input=0;

//     // 값 입력
//     printf("값을 입력하시오 : ");
//     scanf("%d", &input);
//     int check_input;
//     //check_input = getchar(input);
//     //값이 문자인지 숫자인지 판별
//     if(check_input >= '0' && check_input <= '9')
//     {

//         //숫자의 홀짞 판별
//         if(input%2 == 0) // if(input%2 !=1) //첫조건을 홀수로 할때
//         {
//             //결과 출력 1
//             printf("값은 짝수입니다.\n");
//         }
//         else
//         {
//             //결과 출력 2
//             printf("값은 홀수입니다.\n ");
//         }
        
//     }
//     else
//     {
//         //문자일때 출력
        

//         printf("문자는 입력할 수 없습니다.\n");
//     }
    




//     return 0;
// }

/*
    개인 파생 문제 : 입력이 숫자인지 문자인지 판별하여서 출력을 바꾸기.
*/

// #include <stdio.h>
// #include <ctype.h>

// int main(void){

//     //값을 받을 변수 지정
//     int input = 0;//초기화

//     // 값 입력
//     printf("값을 입력하시오 : ");

//     // 문자열을 임시 저장할 공간
//     // 입력받은 값이 임시로 문자열로 저장 후, 
//     // 해당 문자열이 숫자인지 문자인지 판별
//     char buf[64];

//     // 사용자가 입력한 값을 'buf'라는 char형 배열에 저장
//     // 해당 배열을 통해 숫자인지 문자인지 판별
//     if (scanf("%63s", buf) != 1) // 입력 실패 검사
//     {
//         printf("입력을 읽지 못했습니다.\n");
//         return 1;// 
//     }

//     // 값이 숫자인지 판별 (부호 허용)
//     int is_number = 1; // 숫자면 1, 아니면 0
//     int i = 0;

//     // 음수인지 아닌지 기억하기 위한 값
//     int is_negative = 0; // 0: 양수, 1: 음수
//     int value = 0; // 숫자로 변환한 값을 저장

//     /*
//         buf[0]의 의의는 입력을 받은 값이 부호, 즉 -12, -34, -191 와 같은 부호가 붙었을 경우와
//         아닌 경우를 구별하기 위한 조건문.
//     */

//     if (buf[0] == '-' || buf[0] == '+')
//     {
//         is_negative = (buf[0] == '-');
//         i = 1;
//     }
//     /*
//         buf[i]의 의의는 부호만 입력된 경우를 걸러내기 위한 조건문.
//         1234 -> buf[0] = '1', buf[1] = '2', buf[2] = '3', buf[3] = '4', buf[4] = '\0'
//         -1234 -> buf[0] = '-', buf[1] = '1', buf[2] = '2', buf[3] = '3', buf[4] = '4', buf[5] = '\0'
//         위와 같이 1234와 -1234의 경우 부호가 붙었는지 안붙었는지에 따라
//         buf 배열의 인덱스가 달라지기 때문에 이를 구별하기 위한 조건문.
//     */
//     if (buf[i] == '\0')
//     {
//         is_number = 0; // 부호만 입력된 경우
//     }

//     // 입력값이 숫자인지 검사하면서 동시에 숫자로 변환 (한 번의 루프)
//     for (; buf[i] != '\0'; i++)
//     {
//         if (!isdigit((unsigned char)buf[i])) {
//             is_number = 0;
//             break;
//         }
//         value = value * 10 + (buf[i] - '0');
//     }

//     /*
//         is_number는 '입력값이 숫자인가'를 저장하는 변수
//         숫자라면 1, 문자가 섞였거나 문자라면 0
//         if(is_number)는 사실상 if(is_number == 1)과 동일(자주 쓰이는 표현, 중요)
//     */
//     if (is_number)
//     {
//         if (is_negative) //부호가 음수일 때
//         {
//             value = -value;
//         }
//         //변환 결과를 input에 저장. 즉, input이 진짜 정수값이 됨.
//         input = value;

//         // 숫자의 홀짝 판별
//         if (input % 2 == 0) {
//             printf("값은 짝수입니다.\n");
//         } else {
//             printf("값은 홀수입니다.\n");
//         }
//     } 
//     else 
//     {
//         // 문자일 때 출력
//         printf("문자는 입력할 수 없습니다.\n");
//     }

//     return 0;
// }

#include <stdio.h>
#include <ctype.h>

int main(void)
{
    int input = 0;

    printf("값을 입력하시오 : ");

    //문자열 임시 저장 공간
    char buf[64];

    /* 
        정상적으로 문자열 하나를 읽었다면 1을 반환,
        읽지 못했다면 1이 아닌 값을 반환(0이나 EOF).
    */
    if (scanf("%63s", buf) != 1)
    {
        printf("입력을 읽지 못했습니다.\n");
        return 1;
    }

    int is_number = 1;
    int i = 0;

    int is_negative = 0;
    int value = 0;

    if (buf[0] == '-' || buf[0] == '+')//부호가 붙은 경우 // 
    {
        is_negative = (buf[0] == '-');//부호가 붙었는데, 그게 - 이면 1, +이면 0
        i = 1;
    }

    if (buf[i] == '\0')
    {
        is_number = 0;
    }

    for (; buf[i] != '\0'; i++)//'\0' 은 null 문자 의미.
    {
        // isdigit(x)는 x가 숫자('0'~'9')인지 검사
        // 숫자면 1(참), 아니면 0(거짓)
        // isdigit 같은 함수는 음수 값이 들어가면 문제가 생길 수 있어서
        // (unsigned char)로 형변환을 시켜주는 것이 좋음.
        // 즉, 안전하게 0~255 범위로 변환하고 넘기는 습관.
        if (!isdigit((unsigned char)buf[i]))
        {
            is_number = 0;
            break;
        }
        value = value * 10 + (buf[i] - '0');
    }
    // 즉, 해당 코딩의 의미는 "문자열의 끝까지 한글자씩 보면서, 숫자가 아닌 글자가 나오면 그때 처리한다."

    if (is_number)
    {
        if (is_negative)
        {
            value = -value;
        }
        input = value;

        if (input % 2 == 0)
        {
            printf("값은 짝수입니다.\n");
        }
        else
        {
            printf("값은 홀수입니다.\n");
        }
    }
    else
    {
        printf("문자는 입력할 수 없습니다.\n");
    }

    return 0;
}