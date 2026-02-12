/* 문제 요약:

C 이스케이프 시퀀스 목록

\\a   : 경고음(벨)
\\b   : 백스페이스
\\f   : 폼피드(페이지 넘김)
\\n   : 줄바꿈(LF)
\\r   : 캐리지 리턴(CR)
\\t   : 탭(수평)
\\v   : 수직 탭
\\0   : 널 문자(NUL, 문자열 종료)
\\\\   : 역슬래시 문자 자체
\\'   : 작은따옴표 문자
\\"   : 큰따옴표 문자
\\?   : 물음표 문자

\\ooo : 8진수 코드 (예: \\101 = 'A')
\\xhh : 16진수 코드 (예: \\x41 = 'A')

\\uXXXX      : 유니코드 16비트 (예: \\u0041 = 'A')
\\UXXXXXXXX  : 유니코드 32비트 (예: \\U00000041 = 'A')


*/
#define _CRT_SECURE_NO_WARNINGS // 전처리기 세팅
#include <stdio.h>              // 필요시 추가 헤더: <stdlib.h>, <string.h>, <math.h> 등

// 함수 선언

int main(void)
{
    // 선언

    // 입력

    // 처리

    // 출력
    printf("Be happy\n");
    printf("12345678901234567890\n");
    printf("My\tfriend\n");
    printf("Goot\bd\tchance\n"); // 'Goot'를 출력하고 한 칸 왼쪽으로 이동(\b)해 t를 d로 바꾸고 탭 위치로 이동(\t) 후에 "chance"를 출력하고 줄을 바꿈(\n)
    printf("Cow\rW\a\n");        // 맨 앞으로 이동(/r)해 C를 W로 바꾸고 벨소리(\a)를 내고 줄을 바꿈.

    // 함수종료
    return 0;
}

// 함수 정의 (필요 시 주석 해제 후 작성)
/*

*/