/*
   제작 시간 : 0227_11:23
    유형 : 예제
    주제 :
    문제 설명: 구조체 작성해보기
    -
*/

#include <iostream>
#include <iomanip>

typedef struct StudentInfo
{
    char bloodType; // 혈액형
    int stdNum;     // 학번
    float grade;    // 평점
} student;

student std2{'B', 1234, 4.0F};

int main()
{
    student std1{};

    std::cout << "혈액형(A, B, C, D) : ";
    std::cin >> std1.bloodType;
    std::cout << "학번 : ";
    std::cin >> std1.stdNum;
    std::cout << "평점 : ";
    std::cin >> std1.grade;

    std::cout << "혈액형 : " << std1.bloodType << '\n';
    std::cout << "학번 : " << std1.stdNum << '\n';
    std::cout << "평점 : " << std1.grade << '\n'; // std::cout << "평점 : " << std::fixed << std::setprecision(1) << std1.grade << '\n';

    return 0;
}
