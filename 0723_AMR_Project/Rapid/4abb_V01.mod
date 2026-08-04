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
        ! TODO: 4abb의 실제 조립 사이클(예: Run_Assembly_Cycle)이 아직 작성되지
        !       않아서 Start를 받아도 지금은 로그만 남기고 아무 동작도 안 함.
        !       사이클이 완성되면 여기서 그 PROC을 호출하고, 그 사이클의 마지막
        !       동작 직후에 3abb/5abb와 동일하게 SocketSend로 완료 신호를
        !       중앙 서버로 보내도록 맞출 것 (Done 문자열, srv_client_socket 사용).
        IF (StrLen(cmd) >= 5) THEN
            IF (StrPart(cmd, 1, 5) = "Start") OR (StrPart(cmd, 1, 5) = "start") THEN
                TPWrite "Move Start";
                ! TODO: 실제 조립 사이클 PROC 호출 자리
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
