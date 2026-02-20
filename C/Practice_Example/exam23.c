/* 문제 요약:
   - [배열] 문자열을 입력을 받아 (최대 80자)

입력된 글자 중 알파벳 대문자의 개수

소문자의 개수, 특수문자의 개수,

숫자의 개수를 출력하세요.

gets, fgets, scanf로 입력가능, ASCII 코드표 (없어도 가능)

단, 띄워쓰기 없이 연속된 문자열로 입력됩니다.

---------------------------------------------------------

123%$#ABCDxyz

알파벳 대문자 : 4

알파벳 소문자 : 3

숫자 : 3

특수문자 : 3

---> flag변수, cnt변수 ==> 변수를 도구로 사용할 수 있느냐?
*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅

// 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등
#include <stdio.h>
#include <string.h>

// 함수 선언

int main(void)
{
    // 변수 선언 및 초기화
    char str[80];
    int upperCase = 0; // 대문자
    int lowerCase = 0; // 소문자
    int special = 0;   // 특수문자
    int number = 0;    // 숫자
    int sizeLen = 0;
    // 데이터 준비 및 입력
    printf("문자열을 입력하시오 : ");
    scanf("%s", str);

    // 로직 처리
    sizeLen = (int)strlen(str);
    for (int i = 0; i < sizeLen; i++)
    {
        if ('A' <= str[i] && str[i] <= 'Z')
        {
            upperCase++;
        }
        else if ('a' <= str[i] && str[i] <= 'z')
        {
            lowerCase++;
        }
        else if ('0' <= str[i] && str[i] <= '9')
        {
            number++;
        }
        else
        {
            special++;
        }
    }

    // 결과 출력
    printf("대문자 갯수 : %d\n", upperCase);
    printf("소문자 갯수 : %d\n", lowerCase);
    printf("숫자 갯수 : %d\n", number);
    printf("특수문자 갯수 : %d\n", special);

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/
