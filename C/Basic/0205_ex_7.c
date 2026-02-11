#include <stdio.h>

int main()
{
    
    double kor;//한국 점수
    double eng;//영어 점수
    double math;//수학 점수

    double total;//총점
    double average;//평균

    //국어점수
    printf("국어 점수 : ");
    scanf("%lf", &kor);
    if(kor < 0 || kor > 100)
    {
        printf("잘못된 점수입니다. 0~100 사이의 값을 입력하세요.\n");
        return 0;
    }

    //영어점수
    printf("영어 점수 : ");
    scanf("%lf", &eng);
    if(eng < 0 || eng > 100)
    {
        printf("잘못된 점수입니다. 0~100 사이의 값을 입력하세요.\n");
        return 0;
    }


    //수학점수
    printf("수학 점수 : ");
    scanf("%lf", &math);
    if(math < 0 || math > 100)
    {   
        printf("잘못된 점수입니다. 0~100 사이의 값을 입력하세요.\n");
        return 0;
    }

    total = kor + eng + math;
    average = total / 3.0;

    printf("총점 : %.2lf\n", total);
    printf("평균 : %.2lf\n", average);

    return 0;
}