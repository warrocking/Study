MODULE MainModule
    TASK PERS tooldata tool1:=[TRUE,[[3.25653,-2.2499,106.27],[1,0,0,0]],[0.2,[0,0,50],[1,0,0,0],0,0,0]];

    ! ===== Socket server settings (edit these two when reusing this block on another robot) =====
    CONST string ROBOT_IP := "192.168.3.3";
    CONST num ROBOT_PORT := 5000;

    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;

    PROC Main()
        ! Role: Entry point - runs one-time setup, then waits for socket commands forever.
        ! Process: Run_Socket_Server accepts a connector and dispatches whatever it
        !          receives to Handle_Command.
        AccSet 1, 1;
        Run_Socket_Server;
    ENDPROC

    PROC Run_Socket_Server()
        ! Role: Waits for a connector to connect, then repeatedly waits for a command and
        !       dispatches it to Handle_Command. Rebuilds the connection if it drops.
        Start_Server ROBOT_IP, ROBOT_PORT;

        WHILE srv_keep_listening DO
            TPWrite "Waiting for connector...";
            SocketAccept srv_server_socket, srv_client_socket;
            TPWrite "Connector connected. Waiting for commands.";

            WHILE TRUE DO
                SocketReceive srv_client_socket \Str:=srv_received_string;
                TPWrite "Command received: " + srv_received_string;
                Handle_Command srv_received_string;
            ENDWHILE
        ENDWHILE

        ERROR
            IF ERRNO = ERR_SOCK_TIMEOUT THEN
                RETRY;
            ELSEIF ERRNO = ERR_SOCK_CLOSED THEN
                Start_Server ROBOT_IP, ROBOT_PORT;
                SocketAccept srv_server_socket, srv_client_socket;
                RETRY;
            ELSE
                TPWrite "Socket error, ERRNO="\Num:=ERRNO;
                Stop;
            ENDIF
    ENDPROC

    PROC Start_Server(string ip, num port)
        ! Role: (Re)builds the server socket from scratch on the given ip/port.
        Close_All_Sockets;
        SocketCreate srv_server_socket;
        SocketBind srv_server_socket, ip, port;
        SocketListen srv_server_socket;
    ENDPROC

    PROC Close_All_Sockets()
        ! Role: Best-effort close - a socket that was never created raises an error here;
        !       TRYNEXT just skips to the next line instead of stopping the program.
        SocketClose srv_server_socket;
        SocketClose srv_client_socket;
        ERROR
            TRYNEXT;
    ENDPROC

    PROC Handle_Command(string cmd)
        ! Role: Decides what to do for one received command. Matches by PREFIX
        !       (StrPart), not exact equality (=) - SocketReceive can hand back
        !       trailing CR/LF depending on how the connector sends the command,
        !       and an exact match silently fails whenever that happens (this bit
        !       3abb/5abb before - see their Handle_Command for the same fix).
        IF (StrLen(cmd) >= 5) THEN
            IF (StrPart(cmd, 1, 5) = "Start") OR (StrPart(cmd, 1, 5) = "start") THEN
                TPWrite "Move Start";
                Run_Receiving_Cycle;
                RETURN;
            ENDIF
        ENDIF

        IF (StrLen(cmd) >= 3) THEN
            IF (StrPart(cmd, 1, 3) = "End") OR (StrPart(cmd, 1, 3) = "END") THEN
                !TODO
                RETURN;
            ENDIF
        ENDIF

        IF (StrLen(cmd) >= 9) THEN
            IF (StrPart(cmd, 1, 9) = "Emergency") THEN
                !TODO
            ENDIF
        ENDIF
    ENDPROC

    PROC Run_Receiving_Cycle()
        ! Role: 3abb/5abb처럼 한 번 돌고 끝나는 사이클이 아니라, 4abb는 컨베이어
        !       끝에서 물건이 도착할 때마다 계속 받아서 정리해야 하는 역할이라
        !       "Start"를 받으면 여기서 무한 대기에 들어간다. di00~di03 중
        !       하나가 들어오면 그에 맞는 자리로 옮기고, 다시 다음 도착을
        !       기다리는 걸 반복한다 - 이 PROC은 스스로 끝나지 않는다(3abb/5abb
        !       처럼 사이클 끝에 SocketSend "Done"을 보내는 지점이 없는 이유).
        ! Process: WHILE TRUE로 di00_Car_Upper/di01_Car_Lower/di02_Car_Upper1/
        !          di03_Car_Lower1 네 신호를 폴링 - IO공유관리표(4호기 탭)의
        !          "로봇 입력" 이름을 그대로 사용함. 각 신호에 대응하는
        !          Place_* PROC은 아직 좌표(robtarget)가 티칭 안 되어 있어서
        !          지금은 뼈대만 있고 TPWrite로 로그만 남긴다 - 실제 이동은
        !          좌표 티칭 후 채워 넣을 것.
        WHILE TRUE DO
            IF DInput(di00_Car_Upper) = 1 THEN
                Place_Car_Upper;
            ELSEIF DInput(di01_Car_Lower) = 1 THEN
                Place_Car_Lower;
            ELSEIF DInput(di02_Car_Upper1) = 1 THEN
                Place_Car_Upper1;
            ELSEIF DInput(di03_Car_Lower1) = 1 THEN
                Place_Car_Lower1;
            ENDIF

            WaitTime 0.1;
        ENDWHILE
    ENDPROC

    PROC Place_Car_Upper()
        ! TODO: 실제 이동 좌표(robtarget) 티칭 필요 - 예: p_car_upper_pick,
        !       p_car_upper_place. 티칭 전까지는 로그만 남김.
        TPWrite "di00_Car_Upper arrived - placement not yet taught";
    ENDPROC

    PROC Place_Car_Lower()
        ! TODO: 실제 이동 좌표(robtarget) 티칭 필요.
        TPWrite "di01_Car_Lower arrived - placement not yet taught";
    ENDPROC

    PROC Place_Car_Upper1()
        ! TODO: 실제 이동 좌표(robtarget) 티칭 필요.
        TPWrite "di02_Car_Upper1 arrived - placement not yet taught";
    ENDPROC

    PROC Place_Car_Lower1()
        ! TODO: 실제 이동 좌표(robtarget) 티칭 필요.
        TPWrite "di03_Car_Lower1 arrived - placement not yet taught";
    ENDPROC

    PROC Grip_on()
        PulseDO\PLength:=0.2, do00_grip_on;
        WaitDI di00_grip_on_sen,1;
        WaitTime 0.1;
    ENDPROC

    PROC Grip_off()
        PulseDO\PLength:=0.2, do01_grip_off;
        WaitDI di01_grip_off_sen,1;
        WaitTime 0.1;
    ENDPROC

ENDMODULE
