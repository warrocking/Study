#define _WINSOCK_DEPRECATED_NO_WARNINGS // winsock c4996 처리

// 표준 입출력 함수 사용(printf, fputs 등)
#include <stdio.h>
// 표준 라이브러리 함수 사용(exit, atoi 등)
#include <stdlib.h>
// Windows 소켓 API 사용(socket, connect, recv 등)
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib") // ws2_32.lib 라이브러리를 링크

// 에러 발생 시 메시지 출력 후 종료하는 함수 선언
void error_handling(char *message);

int main(int argc, char *argv[])
{
    // WSA(Windows Sockets) 초기화 정보를 담는 구조체
    WSADATA wsaData;
    // 소켓 핸들(통신의 끝점)
    SOCKET hSocket;
    // 서버 주소 정보를 담는 구조체
    SOCKADDR_IN servAddr;

    // 서버로부터 받을 메시지 버퍼
    char message[30];
    // 수신한 바이트 길이
    int strLen = 0;
    int idx = 0, readLen = 0;

    // 프로그램 실행 인자 개수 확인 (IP, port 필요)
    if (argc != 3)
    {
        printf("Usage : %s <IP> <port>\n", argv[0]);
        exit(1);
    }
    // 소켓 라이브러리 초기화
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
        error_handling("WSAStartup() error!");
    // IPv4 + TCP 스트림 소켓 생성 (이 소켓으로 서버에 연결 요청)
    hSocket = socket(PF_INET, SOCK_STREAM, 0);
    if (hSocket == INVALID_SOCKET)
        error_handling("socket() error");

    // 구조체를 0으로 초기화
    memset(&servAddr, 0, sizeof(servAddr));
    // 주소 체계: IPv4
    servAddr.sin_family = AF_INET;
    // 서버 IP 설정 (문자열 -> 네트워크 바이트 순서의 IPv4 주소)
    servAddr.sin_addr.s_addr = inet_addr(argv[1]);
    // 서버 포트 설정 (문자열 -> 정수 -> 네트워크 바이트 순서)
    servAddr.sin_port = htons(atoi(argv[2]));

    // 서버에 연결 요청
    if (connect(hSocket, (SOCKADDR *)&servAddr, sizeof(servAddr)) == SOCKET_ERROR)
        error_handling("connect() error!");
    // recv 호출로 서버가 보낸 데이터를 수신
    while (readLen = recv(hSocket, &message[idx++], 1, 0))
    {
        if (readLen == -1)
            error_handling("read() error!");
        strLen += readLen;
    }
    // recv는 문자열 종료 문자를 자동으로 붙이지 않음(필요 시 직접 추가)
    printf("Message from server: %s \n", message);
    // 소켓 종료
    closesocket(hSocket);
    //
    WSACleanup();
    // 소켓 라이브러리 정리(WSAStartup 해제)
    WSACleanup();

    return 0;
}

void error_handling(char *message)
{
    // 에러 메시지 출력
    fputs(message, stderr);
    fputc('\n', stderr);
    // 비정상 종료
    exit(1);
}
