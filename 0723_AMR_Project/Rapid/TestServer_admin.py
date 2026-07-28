# TestServer_admin.py
#
# 총괄(관리자) 노트북에서 실행하는 테스트 서버.
# 중계기(TestServer_Connector.py) 1대의 접속을 기다렸다가, 접속되면 명령을 입력해서
# 그대로 전송함. 지금은 1:1(중계기 1대) 테스트용이라 접속을 한 번만 받고, 그 뒤로는
# 같은 연결에 계속 명령을 보냄.
#
# 현재 정의된 명령은 "Start" 하나뿐 - 그 외 문자열도 그대로 보내지긴 하지만
# TestServer.mod가 "Start"만 인식하므로 로봇 쪽에서는 무시됨.
#
# 실행 (VSCode 통합 터미널, PowerShell):
#     python TestServer_admin.py

import socket


HOST = "0.0.0.0"   # 모든 인터페이스에서 접속을 받음 - Tailscale, 일반 LAN 둘 다 동작
PORT = 5000
ENCODING = "utf-8"
QUIT_MESSAGE = "/quit"


def send_text(connection, text):
    connection.sendall((text + "\n").encode(ENCODING))


print("테스트 관리자 서버를 시작합니다.")
print(f"대기 포트: {PORT} (모든 네트워크 인터페이스)")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print("중계기 접속을 기다리고 있습니다.")
        connection, address = server_socket.accept()
        print(f"[중계기가 연결되었습니다: {address}]")

        with connection:
            while True:
                command = input("[관리자] 명령 입력 (현재 'Start'만 유효, 종료는 '/quit'): ")

                send_text(connection, command)
                print(f"[전송함] {command}")

                if command == QUIT_MESSAGE:
                    print("[관리자 서버를 종료합니다.]")
                    break

except KeyboardInterrupt:
    print()
    print("관리자 서버를 종료합니다.")

except OSError as error:
    print()
    print("서버 오류:", error)
