
/*
    성적 1개 정수를 입력 받는다(score).
    100점 이하 90점 이상 이면 A,
    90점 미만 80점 이상 이면 B,
    80점 미만 70점 이상 이면 C,
    70점 미만 60점 이상 이면 D,
    60점 미만 이면 F를 출력하는 프로그램을 작성하시오.

    if / else if / else 문을 사용하여 작성하시오.
*/
#include <stdio.h>

int main() 
{
    //변수 지정
    int score;
    char grade;
    // 입력
    printf("성적을 입력하세요(0~100) : ");
    scanf("%d", &score);

    // 1차 조건 - 범위 검사
    if(score < 0 || score > 100)
    {
        printf("잘못된 점수입니다. 0~100 사이의 값을 입력하세요.\n");
        return 0;
    }

    // 2차 조건 - 학점 판별
    if(90<=score && score<=100)
        grade = 'A';
    else if(80<=score && score<90)
        grade = 'B';
    else if(70<=score && score<80)
        grade = 'C';
    else if(60<=score && score<70)
        grade = 'D';
    else
        grade = 'F';

    // 출력
    printf("등급 : %c\n", grade);
    return 0;
}