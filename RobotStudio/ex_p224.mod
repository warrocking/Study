MODULE MainModule
    ! =====================================================================
    ! ex_p224.mod - TCP 소켓 서버 예제
    !
    ! 로봇 컨트롤러가 TCP 서버 역할을 하며, 192.168.3.3:5000 에서 클라이언트
    ! 접속을 기다렸다가 접속되면 문자열 명령을 받아 로봇을 움직이는 예제.
    !
    ! 지원 명령(수신 문자열):
    !   "11" : p10 위치로 이동
    !   "22" : p20 위치로 이동
    !   "33" : p30 위치로 이동
    !   "qq" : 현재 클라이언트와의 통신 루프 종료 (연결 닫고 다음 접속 대기)
    !
    ! 오류 처리:
    !   - 소켓 타임아웃          -> 같은 지점에서 재시도(RETRY)
    !   - 소켓이 예기치 않게 닫힘 -> 소켓을 다시 만들어 재접속 대기 후 재시도
    !   - 그 외 오류             -> 에러 번호 출력 후 프로그램 정지
    ! =====================================================================

    VAR socketdev server_socket;        ! 서버(로봇) 측 소켓 핸들
    VAR socketdev client_socket;        ! 접속한 클라이언트 소켓 핸들
    VAR string received_string;         ! 클라이언트로부터 받은 문자열 저장
    VAR bool keep_listening := TRUE;    ! 서버 유지 여부 (바깥 WHILE 루프 조건)
    VAR robtarget current_p:=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]; ! 명령 수신 시점의 로봇 현재 위치 저장용
    VAR robtarget move_p:=[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];    ! 이동할 목표 위치 계산용
    PERS tooldata tool1:=[TRUE,[[0,0,110],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]]; ! 사용할 툴 데이터
    VAR bool ck_bit := TRUE;            ! 현재 클라이언트와의 통신 유지 여부 (안쪽 WHILE 루프 조건)

    VAR robtarget p10:=[[399.28,-481.10,609.74],[0.000379919,-0.117273,-0.9931,7.17198E-05],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];    ! "11" 명령의 목표 위치 (아직 티칭 안 됨 - 실제 좌표로 바꿔야 함)
    VAR robtarget p20:=[[399.28,-66.83,609.74],[0.000365924,-0.117248,-0.993103,7.73677E-05],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];    ! "22" 명령의 목표 위치 (아직 티칭 안 됨 - 실제 좌표로 바꿔야 함)
    VAR robtarget p30:=[[399.28,417.10,609.71],[0.000373905,-0.117213,-0.993107,9.7879E-05],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];    ! "33" 명령의 목표 위치 (아직 티칭 안 됨 - 실제 좌표로 바꿔야 함)

    PROC main()
        AccSet 1,1;                                     ! 가감속 100%로 설정
        SocketCreate server_socket;                      ! 서버 소켓 생성
        SocketBind server_socket, "192.168.3.3", 5000;    ! 로봇 컨트롤러 IP/포트에 소켓 바인딩
        SocketListen server_socket;                       ! 클라이언트 접속 대기 시작

        WHILE keep_listening DO                            ! 서버 유지: 클라이언트가 끊겨도 계속 새 접속을 받음
            SocketAccept server_socket, client_socket;      ! 클라이언트 접속 수락 (접속될 때까지 대기)
            ck_bit := TRUE;                                 ! 새 클라이언트를 위해 통신 루프 조건 재설정

            WHILE ck_bit DO                                  ! 현재 클라이언트와 통신 유지
                SocketReceive client_socket \Str:=received_string; ! 클라이언트로부터 문자열 수신 (수신될 때까지 대기)
                TPWrite "Client wrote - " + received_string;         ! 티치펜던트에 수신 내용 출력 (디버그용)
                SocketSend client_socket \Str:="Message acknowledged"; ! 수신 확인 응답을 클라이언트로 전송

                IF received_string = "11" THEN                  ! 명령이 "11"이면
                    MoveL Offs(p10, 0, 0, 0), v300, fine, tool1;    ! p10 위치로 이동
                ENDIF

                IF received_string = "22" THEN                  ! 명령이 "22"이면
                    MoveL Offs(p20, 0, 0, 0), v300, fine, tool1;    ! p20 위치로 이동
                ENDIF

                IF received_string = "33" THEN                  ! 명령이 "33"이면
                    MoveL Offs(p30, 0, 0, 0), v300, fine, tool1;    ! p30 위치로 이동
                ENDIF

                IF received_string = "qq" THEN                  ! 명령이 "qq"(종료)이면
                    ck_bit := FALSE;                               ! 안쪽 통신 루프 종료 -> 이 클라이언트 연결을 닫으러 감
                ENDIF

                received_string := "";                            ! 다음 수신을 위해 문자열 버퍼 초기화
            ENDWHILE

            SocketClose client_socket;                          ! 현재 클라이언트 소켓 닫기 (다음 접속을 다시 대기)
        ENDWHILE

        SocketClose server_socket;                            ! 서버 소켓 닫기 (정상 종료 시)

        ERROR                                                  ! ---- 에러 핸들러 ----
        IF ERRNO=ERR_SOCK_TIMEOUT THEN                         ! 소켓 타임아웃 에러면
            RETRY;                                                ! 에러 발생 직전 명령부터 재시도
        ELSEIF ERRNO=ERR_SOCK_CLOSED THEN                      ! 소켓이 예기치 않게 닫힌 에러면
            SocketClose server_socket;                            ! 기존 서버 소켓 정리
            SocketClose client_socket;                            ! 기존 클라이언트 소켓 정리
            SocketCreate server_socket;                           ! 서버 소켓 재생성
            SocketBind server_socket, "192.168.3.3", 5000;        ! 같은 IP/포트로 재바인딩
            SocketListen server_socket;                           ! 재접속 대기 시작
            SocketAccept server_socket, client_socket;            ! 새 클라이언트 접속 수락
            RETRY;                                                ! 에러 발생 직전 명령부터 재시도
        ELSE                                                    ! 그 외 알 수 없는 에러면
            TPWrite "ERRNO = "\Num:=ERRNO;                        ! 에러 번호를 티치펜던트에 출력
            Stop;                                                  ! 프로그램 정지
        ENDIF
    ENDPROC
ENDMODULE
