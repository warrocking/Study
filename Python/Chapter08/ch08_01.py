"""
    제작 시간 : 0317_14:05
    유형 : 예제
    주제 : 
    문제 설명 : 
    - 
"""

# 기본 모듈
import sys

# 추가 모듈 (필요 시 주석 해제)
# import math
# import itertools
# import collections

# 함수 선언/정의 (필요 시 작성)
# def helper():
#     pass
class Student():#object = 최상위 클래스를 받았다는 얘기
    
    def __init__(self, name, korean, math, english, science):
        super().__init__()
        self.name = name
        self.korean = korean
        self.math = math
        self.english = english
        self.science = science
    
    def get_sum(self):
        return self.korean + self.math + self.english + self.science
    
    def get_average(self):
        return self.get_sum()/4
    
    def to_string(self):
        return "{}\t{}\t{}".format(\
            self.name,\
            self.get_sum(),\
            self.get_average())
    
    
    
    
    
    # student[0].name
    # student[0].korean
    # student[0].math
    # student[0].english
    # student[0].science
    
    
    def make(self):
        self.name = "Brain"
        self.id = 1000
        print("Hello")
        pass
    
    pass

def main() -> None:
    
    # student1 = Student(name = "KarL", id = 1004)
    # student2 = Student(name = "Brain", id = 999)
    # student3 = Student(name = "Yuna", id = 100)
    # student1.make()
    # print(student1.name)
    # student1.name = "Brian"
    # student2.make()    
    students = [
        Student("윤인성", 87, 98, 88, 95),
        Student("연하진", 92, 98, 96, 98),
        Student("구지연", 76, 96, 94, 90),
        Student("나선주", 98, 92, 96, 92),
        Student("윤아린", 95, 98, 98, 98),
        Student("윤명월", 64, 88, 92, 92)        
    ]
    
    print("이름", "총점", "평균", seq = "\t")
    for student in students:
        print(Student.to_string())
        
    
    pass


if __name__ == "__main__":
    main()