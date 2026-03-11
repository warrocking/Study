#define _WINSOCK_DEPRECATED_NO_WARNINGS // winsock c4996 처리

#include <stdio.h>
#include <stdlib.h>
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib") // ws2_32.lib 라이브러리를 링크
void error_handling(char *message);

int main(int argc, char *argv[])
{
    WSADATA wsaData;
    SOCKET hServSock, hClntSock;
    SOCKADDR_IN servAddr, clntAddr;

    int szClntAddr;
    char message[] = "제발 연결되라 제발";

    if (argc != 2)
    {
        printf("Usage : %s <port>\n", argv[0]);
        exit(1);
    }

    // 소캣 라이브러리 초기화
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
        error_handling("WSAStartup() error!");

    // 소캣 생성 -> 37행
    hServSock = socket(PF_INET, SOCK_STREAM, 0);
    if (hServSock == INVALID_SOCKET)
        error_handling("socket() error");

    memset(&servAddr, 0, sizeof(servAddr));
    servAddr.sin_family = AF_INET;
    servAddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servAddr.sin_port = htons(atoi(argv[1]));

    // 26행에서 만든 소켓에서 IP주소와 PORT번호를 할당하고 있다.
    if (bind(hServSock, (SOCKADDR *)&servAddr, sizeof(servAddr)) == SOCKET_ERROR)
        error_handling("bind() error");

    if (listen(hServSock, 5) == SOCKET_ERROR)
        error_handling("listen() error");

    szClntAddr = sizeof(clntAddr);

    // 클라이언트의 연결요청을 수락하기 위해서 accept 함수를 호출하고 있음.
    hClntSock = accept(hServSock, (SOCKADDR *)&clntAddr, &szClntAddr);
    if (hClntSock == INVALID_SOCKET)
        error_handling("accept() error");

    // send 함수 호출을 통해서 accept 쪽에서 연결된 클라이언트에 데이터를 전송하고 있음.
    send(hClntSock, message, sizeof(message), 0);
    closesocket(hClntSock);
    closesocket(hServSock);

    // 프로그램을 종료하기 전에 23줄의 초기화한 소켓 라이브러리를 해제.
    WSACleanup();
    return 0;
}

void error_handling(char *message)
{
    fputs(message, stderr);
    fputc('\n', stderr);
    exit(1);
}