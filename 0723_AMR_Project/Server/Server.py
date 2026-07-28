import socket


HOST = "127.0.0.1"
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


print("중앙 서버를 시작합니다.")
print(f"로컬 주소: {HOST}:{PORT}")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print("접속자를 기다리고 있습니다.")

        while True:
            connection, address = server_socket.accept()

            print()
            print("[접속자가 연결되었습니다.]")

            with connection:
                reader = connection.makefile(
                    "r",
                    encoding=ENCODING,
                    newline="\n",
                )

                while True:
                    received = receive_text(reader)

                    if received is None:
                        print("[접속이 종료되었습니다.]")
                        break

                    print()
                    print(f"[접속자] {received}")

                    if received == QUIT_MESSAGE:
                        print("[접속자가 대화를 종료했습니다.]")
                        break

                    reply = input("[중앙] ")

                    send_text(connection, reply)

                    if reply == QUIT_MESSAGE:
                        print("[중앙 서버가 대화를 종료했습니다.]")
                        break

            print("새로운 접속자를 기다립니다.")

except KeyboardInterrupt:
    print()
    print("중앙 서버를 종료합니다.")

except OSError as error:
    print()
    print("서버 오류:", error)