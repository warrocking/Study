/*
   제작 시간 : 0227_21:30
   유형 : 과제
   주제 : 콘솔 유틸리티
   설명 :
   - 콘솔 화면을 지우는 공통 기능을 제공한다.
   - Windows는 WinAPI로 화면을 초기화하고, 그 외 환경은 clear 명령을 사용한다.
   - 공통 입력 유틸(Y/N, 양의 정수)을 제공한다.
   - Display/Payment/ProjectManager에서 공통으로 사용한다.
*/

#include "ConsoleUtil.h" // 콘솔 유틸 선언 (ClearScreen, ReadMaskedInput, PromptYesNo, PromptPositiveInt)

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h> // 콘솔 제어 (GetStdHandle, FillConsoleOutputCharacter)
#include <conio.h>   // 키 입력 ( _getch )
#else
#include <cstdlib>  // system("clear")
#endif
#include <iostream> // 마스킹 출력 (std::cout)

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

std::string ReadMaskedInput(size_t maxLen, bool digitsOnly)
{
#ifdef _WIN32
    std::string out;
    while (true)
    {
        int ch = _getch();
        if (ch == '\r') // Enter
            break;
        if (ch == '\b') // Backspace
        {
            if (!out.empty())
            {
                out.pop_back();
                std::cout << "\b \b";
            }
            continue;
        }

        if (maxLen > 0 && out.size() >= maxLen)
            continue;
        if (digitsOnly && (ch < '0' || ch > '9'))
            continue;

        out.push_back(static_cast<char>(ch));
        std::cout << '*';
    }
    std::cout << "\n";
    return out;
#else
    std::string out;
    std::cin >> out;
    return out;
#endif
}

bool ReadLineStrict(std::string &out)
{
    out.clear();
    if (!std::getline(std::cin, out))
    {
        std::cin.clear();
        return false;
    }
    if (out.empty())
        return false;
    return true;
}

bool TryParseIntExact(const std::string &s, int &out)
{
    if (s.empty())
        return false;
    for (char c : s)
    {
        if (c < '0' || c > '9')
            return false;
    }
    try
    {
        out = std::stoi(s);
    }
    catch (...)
    {
        return false;
    }
    return true;
}

bool PromptYesNo(const std::string &prompt, bool silentOnInvalid)
{
    while (true)
    {
        if (!prompt.empty())
            std::cout << prompt << "\n";
        std::cout << "입력 : ";
        std::string line;
        if (!ReadLineStrict(line))
            continue;
        if (line == "Y" || line == "y")
            return true;
        if (line == "N" || line == "n")
            return false;
        if (!silentOnInvalid)
            std::cout << "Y 또는 N만 입력하세요.\n";
    }
}

bool PromptPositiveInt(const std::string &prompt, int &out, bool silentOnInvalid)
{
    while (true)
    {
        if (!prompt.empty())
            std::cout << prompt << "\n";
        std::cout << "입력 : ";
        std::string line;
        if (!ReadLineStrict(line))
            continue;
        int v = 0;
        if (TryParseIntExact(line, v) && v > 0)
        {
            out = v;
            return true;
        }
        if (!silentOnInvalid)
            std::cout << "1 이상의 숫자만 입력하세요.\n";
    }
}
