MODULE MainModule
    ! =====================================================================
    ! TestServer.mod - reusable socket-server building block
    !
    ! Designed to be copy-pasted as-is into other RAPID modules
    ! (Car_Assembly_5abb..., Car_Assembly_3abb2...). To reuse it there:
    !   1) Copy the CONST/VAR block below and the 4 PROCs
    !      (Run_Socket_Server, Start_Server, Handle_Command, Close_All_Sockets)
    !      unchanged - the "srv_" prefix keeps them from clashing with
    !      that module's own variable names.
    !   2) Set ROBOT_IP / ROBOT_PORT for that robot.
    !   3) Replace the body of Handle_Command with calls to that module's
    !      own production PROCs instead of the example MoveL.
    !   4) Call Run_Socket_Server; once from that module's own Main()
    !      (in Car_Assembly_5abb_version02.mod this is exactly where the
    !      "Placeholder: TCP server code goes here" comment already is).
    ! No other part of Main() needs to change.
    ! =====================================================================

    CONST string ROBOT_IP := "192.168.3.3";
    CONST num ROBOT_PORT := 5000;

    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;

    TASK PERS tooldata tool1 := [TRUE, [[3.25653, -2.2499, 106.27], [1, 0, 0, 0]], [0.2, [0, 0, 50], [1, 0, 0, 0], 0, 0, 0]];

    ! Example target - same value as p_assembly in Car_Assembly_5abb_version02.mod
    PERS robtarget p_assembly := [
    [342.30, -38.16, 327.52],
    [1.20614E-05, 0.456804, -0.889567, -5.42704E-06],
    [-1, -1, -1, 0],
    [9E+09, 9E+09, 9E+09, 9E+09, 9E+09, 9E+09]
    ];
    VAR speeddata v_moveSpeed := v200;

    PROC Main()
        AccSet 1, 1;
        Run_Socket_Server;
    ENDPROC

    ! Role: waits for one connector, then repeatedly waits for a command and
    ! dispatches it to Handle_Command. Rebuilds the connection on disconnect.
    PROC Run_Socket_Server()
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

    ! Role: (re)builds the server socket from scratch on the given ip/port.
    PROC Start_Server(string ip, num port)
        Close_All_Sockets;
        SocketCreate srv_server_socket;
        SocketBind srv_server_socket, ip, port;
        SocketListen srv_server_socket;
    ENDPROC

    ! Role: the ONLY part to customize per robot/module - decide what each
    ! received command does. Replace the body with calls to this module's
    ! own production PROCs (e.g. Run_Assembly_Cycle) as more commands are added.
    PROC Handle_Command(string cmd)
        IF StrLen(cmd) >= 5 THEN
            IF StrPart(cmd, 1, 5) = "Start" THEN
                MoveL p_assembly, v_moveSpeed, fine, tool1;
                TPWrite "Move done";
            ENDIF
        ENDIF
    ENDPROC

    ! Role: best-effort close - a socket that was never created raises an
    ! error here; TRYNEXT just skips to the next line instead of stopping.
    PROC Close_All_Sockets()
        SocketClose srv_server_socket;
        SocketClose srv_client_socket;
        ERROR
            TRYNEXT;
    ENDPROC

ENDMODULE
