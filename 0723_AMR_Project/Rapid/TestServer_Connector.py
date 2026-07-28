# TestServer_Connector.py
#
# 중계기(옆 노트북)에서 실행하는 테스트 클라이언트.
# 역할이 두 가지지만 순차적으로 처리함(스레드 불필요):
#   1) ABB 로봇(TestServer.mod)에 클라이언트로 접속
#   2) 총괄 관리자 서버(TestServer_admin.py)에 클라이언트로 접속
# 이후로는 "관리자에게서 명령을 받으면 그 즉시 같은 명령을 ABB로 그대로 전달"만
# 반복하는 단순 중계 루프. ABB는 별도 응답을 보내지 않으므로(TestServer.mod 참고)
# 이 스크립트도 ABB로부터 뭔가를 읽어오지 않음.
#
# 실행 전 아래 두 주소를 실제 환경에 맞게 확인/수정하세요.

import socket


ABB_HOST = "192.168.3.3"   # ABB 로봇의 서버 IP (project.mod/ex_p224.mod와 동일)
ABB_PORT = 5000

ADMIN_HOST = "100.109.178.123"   # 총괄 노트북의 Tailscale IP - 실제 환경에 맞게 수정
ADMIN_PORT = 5000

ENCODING = "utf-8"
QUIT_MESSAGE = "/quit"


def send_text(connection, text):
    connection.sendall((text + "\n").encode(ENCODING))


def receive_text(reader):
    line = reader.readline()
    if line == "":
        return None
    return line.rstrip("\r\n")


print("중계기 프로그램을 시작합니다.")

print(f"ABB 로봇에 접속합니다: {ABB_HOST}:{ABB_PORT}")
try:
    abb_connection = socket.create_connection((ABB_HOST, ABB_PORT), timeout=10)
except ConnectionRefusedError:
    print("ABB 로봇이 연결을 거부했습니다. TestServer.mod가 실행 중인지 확인하세요.")
    raise SystemExit(1)
except OSError as error:
    print("ABB 로봇 연결 오류:", error)
    raise SystemExit(1)

abb_connection.settimeout(None)   # 연결 후에는 타임아웃 없이 계속 대기 가능하게 해제
print("[ABB 로봇에 연결되었습니다.]")

print(f"관리자 서버에 접속합니다: {ADMIN_HOST}:{ADMIN_PORT}")
try:
    admin_connection = socket.create_connection((ADMIN_HOST, ADMIN_PORT), timeout=10)
except ConnectionRefusedError:
    print("관리자 서버가 연결을 거부했습니다. TestServer_admin.py가 실행 중인지 확인하세요.")
    abb_connection.close()
    raise SystemExit(1)
except OSError as error:
    print("관리자 서버 연결 오류:", error)
    abb_connection.close()
    raise SystemExit(1)

admin_connection.settimeout(None)   # 관리자가 명령을 오래 안 보내도 타임아웃 나지 않게 해제
print("[관리자 서버에 연결되었습니다.]")
print("이제부터 관리자 명령을 그대로 ABB로 전달합니다.")

admin_reader = admin_connection.makefile("r", encoding=ENCODING, newline="\n")

try:
    while True:
        command = receive_text(admin_reader)

        if command is None:
            print("[관리자 서버와의 연결이 종료되었습니다.]")
            break

        print(f"[관리자] {command}")

        send_text(abb_connection, command)
        print(f"[ABB로 전달함] {command}")

        if command == QUIT_MESSAGE:
            print("[중계기를 종료합니다.]")
            break

except KeyboardInterrupt:
    print()
    print("중계기를 종료합니다.")

except OSError as error:
    print()
    print("중계 중 연결 오류:", error)

finally:
    admin_connection.close()
    abb_connection.close()
