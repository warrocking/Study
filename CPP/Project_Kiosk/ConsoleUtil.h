#pragma once

#include <string>

// 콘솔 유틸 (화면 지우기)
void ClearScreen();
// 마스킹 입력(비밀번호/카드번호 등)
std::string ReadMaskedInput(size_t maxLen, bool digitsOnly);
// 한 줄 입력(빈 입력은 false)
bool ReadLineStrict(std::string &out);
// 숫자만으로 구성된 정수 파싱
bool TryParseIntExact(const std::string &s, int &out);
// Y/N 입력 처리
bool PromptYesNo(const std::string &prompt, bool silentOnInvalid = false);
// 1 이상 정수 입력 처리
bool PromptPositiveInt(const std::string &prompt, int &out, bool silentOnInvalid = false);
