MODULE MainModule
    ! =====================================================================
    ! TestServer.mod - minimal socket-server test module
    !
    ! Standalone test program (not loaded together with Car_Assembly_5abb...).
    ! On startup, closes any leftover sockets first (avoids the small
    ! reconnect glitches that show up if a socket from a previous run is
    ! still half-open), then waits for TestServer_Connector.py to connect.
    ! Once connected, waits for text commands. Only "Start" is defined
    ! right now - it runs one example MoveL to p_assembly (taken from
    ! Car_Assembly_5abb_version02.mod's real taught point).
    ! =====================================================================

    VAR socketdev server_socket;
    VAR socketdev client_socket;
    VAR string received_string;
    VAR bool keep_listening := TRUE;

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
        Close_All_Sockets;

        AccSet 1, 1;
        SocketCreate server_socket;
        SocketBind server_socket, "192.168.3.3", 5000;
        SocketListen server_socket;

        WHILE keep_listening DO
            TPWrite "Waiting for connector...";
            SocketAccept server_socket, client_socket;
            TPWrite "Connector connected. Waiting for commands.";

            WHILE TRUE DO
                SocketReceive client_socket \Str:=received_string;
                TPWrite "Command received: " + received_string;

                ! Compare only the first 5 characters - a trailing \r or \n from the
                ! sender would otherwise make an exact-string match silently fail.
                IF StrLen(received_string) >= 5 THEN
                    IF StrPart(received_string, 1, 5) = "Start" THEN
                        MoveL p_assembly, v_moveSpeed, fine, tool1;
                        TPWrite "Move done";
                    ENDIF
                ENDIF
            ENDWHILE
        ENDWHILE

        ERROR
            IF ERRNO = ERR_SOCK_TIMEOUT THEN
                RETRY;
            ELSEIF ERRNO = ERR_SOCK_CLOSED THEN
                Close_All_Sockets;
                SocketCreate server_socket;
                SocketBind server_socket, "192.168.3.3", 5000;
                SocketListen server_socket;
                SocketAccept server_socket, client_socket;
                RETRY;
            ELSE
                TPWrite "Socket error, ERRNO="\Num:=ERRNO;
                Stop;
            ENDIF
    ENDPROC

    PROC Close_All_Sockets()
        ! Best-effort close - a socket that was never created raises an
        ! error here; TRYNEXT just skips to the next line instead of
        ! stopping the program.
        SocketClose server_socket;
        SocketClose client_socket;
        ERROR
            TRYNEXT;
    ENDPROC

ENDMODULE
