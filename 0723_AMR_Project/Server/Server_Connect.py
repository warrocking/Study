import socket


HOST = "100.109.178.123"
PORT = 5000
ENCODING = "utf-8"
QUIT_MESSAGE = "/quit"


def send_text(connection, text):
    message = text + "\n"
    connection.sendall(message.encode(ENCODING))


def receive_text(reader):
    line = reader.readline()

    if line == "":
        return None

    return line.rstrip("\r\n")


print("접속자 프로그램을 시작합니다.")
print(f"중앙 서버 주소: {HOST}:{PORT}")

try:
    with socket.create_connection((HOST, PORT), timeout=10) as connection:
        # 연결 후에는 답변을 오래 기다려도 시간 초과되지 않게 설정
        connection.settimeout(None)

        print("[중앙 서버에 연결되었습니다.]")

        reader = connection.makefile(
            "r",
            encoding=ENCODING,
            newline="\n",
        )

        while True:
            message = input("[접속자] ")

            send_text(connection, message)

            if message == QUIT_MESSAGE:
                print("[접속자 프로그램을 종료합니다.]")
                break

            received = receive_text(reader)

            if received is None:
                print("[중앙 서버와의 연결이 종료되었습니다.]")
                break

            print(f"[중앙] {received}")

            if received == QUIT_MESSAGE:
                print("[중앙 서버가 대화를 종료했습니다.]")
                break

except socket.timeout:
    print("중앙 서버 연결 시간이 초과되었습니다.")

except ConnectionRefusedError:
    print("중앙 서버가 연결을 거부했습니다.")
    print("중앙 노트북에서 Server.py가 실행 중인지 확인하세요.")

except OSError as error:
    print("연결 오류:", error)