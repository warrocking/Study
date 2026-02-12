#include <stdio.h>  // printf, scanf, fgets 사용을 위한 표준 입출력 헤더

int main(void)
{
    char str1[100], str2[100];  // 입력 문자열과 변환 결과 문자열
    int mode;                   // 0: 소문자->대문자, 1: 대문자->소문자

    printf("문장 입력 : ");     // 사용자에게 입력 안내 메시지 출력
    if (fgets(str1, sizeof str1, stdin) == NULL)  // 한 줄 입력 받기(안전하게 크기 제한)
    {
        return 0;               // 입력 실패 시 종료
    }

    int i = 0;                  // 문자열 인덱스 변수
    while (str1[i] != '\0')     // 문자열 끝('\0')까지 순회
    {
        if (str1[i] == '\n')    // 입력의 끝에 포함된 개행 문자 제거
        {
            str1[i] = '\0';     // 개행을 문자열 끝으로 변경
            break;              // 개행을 만나면 반복 종료
        }
        i++;                    // 다음 문자로 이동
    }

    printf("0이면 소문자->대문자, 1이면 대문자->소문자 : ");  // 변환 모드 안내
    if (scanf("%d", &mode) != 1 || (mode != 0 && mode != 1))    // 0 또는 1만 허용
    {
        return 0;               // 잘못된 입력이면 종료
    }

    i = 0;                      // 인덱스를 처음으로 되돌림
    while (str1[i] != '\0')     // 문자열을 끝까지 순회하며 변환 수행
    {
        if (mode == 0 && str1[i] >= 'a' && str1[i] <= 'z')      // 소문자를 대문자로
        {
            str2[i] = str1[i] - /* ('a' - 'A') */0x20;                   // ASCII 간격만큼 빼기
        } 
        else if (mode == 1 && str1[i] >= 'A' && str1[i] <= 'Z') // 대문자를 소문자로
        {
            str2[i] = str1[i] + /* ('a' - 'A') */0x20;                   // ASCII 간격만큼 더하기
        } 
        else 
        {
            str2[i] = str1[i];    // 해당 조건이 아니면 원래 문자 그대로 복사
        }
        i++;                      // 다음 문자로 이동
    }
    str2[i] = '\0';               // 변환 결과 문자열 끝 표시

    printf("str 1 : %s\n", str1); // 원본 문자열 출력
    printf("str 2 : %s\n", str2); // 변환된 문자열 출력

    return 0;                     // 프로그램 정상 종료
}
