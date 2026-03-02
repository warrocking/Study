/*
   제작 시간 : 0227_21:30
   유형 : 과제
   주제 : 콘솔 유틸리티
   설명 :
   - 콘솔 화면을 지우는 공통 기능을 제공한다.
   - Windows는 WinAPI로 화면을 초기화하고, 그 외 환경은 clear 명령을 사용한다.
   - Display/Payment/ProjectManager에서 공통으로 사용한다.
*/

#include "ConsoleUtil.h" // 콘솔 유틸 선언 (ClearScreen)

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h> // 콘솔 제어 (GetStdHandle, FillConsoleOutputCharacter)
#else
#include <cstdlib> // system("clear")
#endif

void ClearScreen()
{
#ifdef _WIN32
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    if (hOut == INVALID_HANDLE_VALUE)
        return;
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    if (!GetConsoleScreenBufferInfo(hOut, &csbi))
        return;

    DWORD cellCount = static_cast<DWORD>(csbi.dwSize.X) * static_cast<DWORD>(csbi.dwSize.Y);
    DWORD count = 0;
    COORD homeCoords = {0, 0};
    FillConsoleOutputCharacter(hOut, ' ', cellCount, homeCoords, &count);
    FillConsoleOutputAttribute(hOut, csbi.wAttributes, cellCount, homeCoords, &count);
    SetConsoleCursorPosition(hOut, homeCoords);
#else
    system("clear"); // Linux/Mac
#endif
}
