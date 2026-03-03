# 이 프로젝트를 빌드하기 위해 필요한 최소 CMake 버전을 지정
cmake_minimum_required(VERSION 3.16)

# 프로젝트 이름을 Project_Kiosk로 지정. LANGUAGES CXX는 C++ 프로젝트라는 뜻.
project(Project_Kiosk LANGUAGES CXX)

#이 프로젝트의 C++ 표준을 C++17로 사용하겠다는 뜻
set(CMAKE_CXX_STANDARD 17)
#C++17이 강제로 적용되도록 세팅하는 코드
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 메인 실행 파일 (ProjectManager 중심) #실행 파일을 하나 만든다는 뜻
#이름은 ProjectManager.exe가 됨.
#괄호 안의 .cpp 파일들을 모두 묶어 컴파일 + 링크함.
add_executable(ProjectManager
  ProjectManager.cpp
  Login.cpp
  Display_selling.cpp
  Display_Manager.cpp
  Payment.cpp
  Shpping.cpp
  ConsoleUtil.cpp
  DataManager.cpp
)
