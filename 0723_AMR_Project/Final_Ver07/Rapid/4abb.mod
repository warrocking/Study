MODULE MainModule

    !========================
    ! Tool & Target Data
    !========================
    TASK PERS tooldata tool3:=[TRUE,[[0,0,160],[1,0,0,0]],[0.1,[0,0,80],[1,0,0,0],0,0,0]];
    
    PERS robtarget pHome := [[418.54,13.35,488.86],[6.30814E-07,0.40512,0.914264,8.9329E-07],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    ! 1? ??? ??
    PERS robtarget UPick_Approach := [[574.60,395.73,396.99],[0.000517249,0.395858,0.918311,0.000210904],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget LPick_Approach := [[573.31,397.72,358.58],[0.000237711,0.401524,0.915848,0.000169236],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget UPick := [[574.60,395.73,294.99],[0.000518894,0.395861,0.91831,0.000211836],[0,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget LPick := [[575.22,399.41,215.63],[0.000186645,-0.40472,-0.914441,0.000143548],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget Upper_Approach := [[451.35,-5.97,252.56],[0.000499126,0.395868,0.918307,0.000203599],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget Upper_Place := [[451.26,-13.32,208.31],[0.000392979,0.39586,0.918311,0.000143316],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget Lower_Approach := [[450.20,-243.65,409.80],[0.000262215,0.396338,0.918105,0.000264412],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget Lower_Place := [[451.55,-237.97,154.59],[0.00018523,0.397531,0.917589,0.000272469],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    ! 2? ??? ??
    PERS robtarget Upper_Approach1 := [[624.28,-5.39,255.37],[2.75122E-05,-0.403898,-0.914804,4.10456E-05],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget Upper_Place1 := [[626.10,-7.47,210.46],[0.000313177,0.400084,0.916478,0.000153992],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget Lower_Approach1 := [[626.39,-243.01,337.30],[0.000429168,-0.349997,-0.936751,0.000207593],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS robtarget Lower_Place1 := [[624.34,-242.95,156.14],[0.000502711,-0.406703,-0.91356,0.000223508],[-1,-1,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    !========================
    ! Interrupt Variables
    !========================
    VAR intnum int_plc_stop;

    !========================
    ! Server (same pattern as 3abb/5abb)
    !========================
    ! 4abb 컨트롤러 자신의 실제 LAN 주소 (펜던트 제어판 > 구성 > Communication >
    ! IP Setting에서 확인함). 3abb/5abb는 192.168.3.3, 4abb는 192.168.3.2로
    ! 서로 다른 주소를 씀 - SocketBind는 컨트롤러 자신의 주소만 허용하므로
    ! 이전에 넣었던 Tailscale 주소(100.102.179.115)는 맞지 않았음.
    CONST string ROBOT_IP := "192.168.3.2";
    CONST num ROBOT_PORT := 5000;

    VAR socketdev srv_server_socket;
    VAR socketdev srv_client_socket;
    VAR string srv_received_string;
    VAR bool srv_keep_listening := TRUE;

    !========================
    ! Main Routine
    !========================
    PROC Main()

        IDelete int_plc_stop;
        CONNECT int_plc_stop WITH Trap_PLC_Stop;
        ISignalDI di05_interrupt, 1, int_plc_stop;
        IWatch int_plc_stop;



        MoveL pHome, v200, z10, tool3;

        Run_Socket_Server;

    ENDPROC

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

    PROC Start_Server(string ip, num port)

        Close_All_Sockets;
        SocketCreate srv_server_socket;
        SocketBind srv_server_socket, ip, port;
        SocketListen srv_server_socket;
    ENDPROC

    PROC Close_All_Sockets()

        SocketClose srv_server_socket;
        SocketClose srv_client_socket;
        ERROR
            TRYNEXT;
    ENDPROC

    PROC Handle_Command(string cmd)
        IF (StrLen(cmd) >= 5) THEN
            IF (StrPart(cmd, 1, 5) = "Start") OR (StrPart(cmd, 1, 5) = "start") THEN
                TPWrite "Move Start";
                Run_Receiving_Cycle;
                RETURN;
            ENDIF
        ENDIF
    ENDPROC

    PROC Run_Receiving_Cycle()

        WHILE TRUE DO

            IF di00_Car_Upper = 1 THEN
                Upper_Move;
                WaitDi di00_Car_Upper, 0;
            ENDIF

            IF di01_Car_Lower = 1 THEN
                Lower_Move;
                WaitDi di01_Car_Lower, 0;
            ENDIF

            IF di02_Car_Upper = 1 THEN
                Upper_Move1;
                WaitDi di02_Car_Upper, 0;
            ENDIF

            IF di03_Car_Lower = 1 THEN
                Lower_Move1;
                WaitDi di03_Car_Lower, 0;
            ENDIF

        ENDWHILE

    ENDPROC


    !========================
    ! Grip Control
    !========================
    PROC Grip_On()
        PulseDO\PLength:=0.2, do00_Grip_On;
    ENDPROC

    PROC Grip_Off()
        PulseDO\PLength:=0.2, do01_Grip_Off;
    ENDPROC

    !========================
    ! Upper_Move
    !========================
    
    PROC Upper_Move()
        MoveL UPick_Approach, v200, z10, tool3;
        MoveL UPick, v50, fine, tool3;
        Grip_On;
        WaitTime 0.3;
        MoveL UPick_Approach, v100, z10, tool3;
        MoveL Upper_Approach, v200, z10, tool3;
        MoveL Upper_Place, v50, fine, tool3;
        Grip_Off;
        WaitTime 0.3;
        MoveL pHome, v200, fine, tool3;
        PulseDO \PLength:=0.2, do02_R_conveyor;
    ENDPROC

    !========================
    ! Lower_Move
    !========================
    
    PROC Lower_Move()
        MoveL LPick_Approach, v200, z10, tool3;
        MoveL LPick, v50, fine, tool3;
        Grip_On;
        WaitTime 0.3;
        MoveL LPick_Approach, v100, z10, tool3;
        MoveL Lower_Approach, v200, z10, tool3;
        MoveL Lower_Place, v50, fine, tool3;
        Grip_Off;
        WaitTime 0.3;
        MoveL Lower_Approach, v200, z10, tool3;
        MoveL pHome, v200, fine, tool3;
        PulseDO \PLength:=0.2, do02_R_conveyor;
    ENDPROC
    
    !========================
    ! Upper_Move1
    !========================
    PROC Upper_Move1()
        MoveL UPick_Approach, v200, z10, tool3;
        MoveL UPick, v50, fine, tool3;
        Grip_On;
        WaitTime 0.3;
        MoveL UPick_Approach, v100, z10, tool3;
        MoveL Upper_Approach1, v200, z10, tool3;
        MoveL Upper_Place1, v50, fine, tool3;
        Grip_Off;
        WaitTime 0.3;
        MoveL pHome, v200, fine, tool3;
        PulseDO \PLength:=0.2, do02_R_conveyor;
    ENDPROC

    !========================
    ! Lower_Move1
    !========================
    PROC Lower_Move1()
        MoveL LPick_Approach, v200, z10, tool3;
        MoveL LPick, v50, fine, tool3;
        Grip_On;
        WaitTime 0.3;
        MoveL LPick_Approach, v100, z10, tool3;
        MoveL Lower_Approach1, v200, z10, tool3;
        MoveL Lower_Place1, v50, fine, tool3;
        Grip_Off;
        WaitTime 0.3;
        MoveL Lower_Approach1, v200, z10, tool3;
        MoveL pHome, v200, fine, tool3;
        PulseDO \PLength:=0.2, do02_R_conveyor;
    ENDPROC
    
    !========================
    ! TRAP Routine (???? ?? ?? - ?? ??)
    !========================
    TRAP Trap_PLC_Stop
        VAR robtarget p_curr;
        StopMove \Quick;       ! 1. ??? ?? ???? ?? ??????.
        StorePath;             ! 2. ?? ?? ??? ???? ?????.
        p_curr := CRobT();     ! 3. ?? ??? ?? ??? ??? ?????.
        
        MoveJ pHome, v200, z50, tool3; ! 4. ??? Home ??? ??????.
        
        ! 5. PLC?? ??? ??(di04_restart)? ??? ??? ?????.
        WaitDI di04_restart, 1; 
        
        MoveL p_curr, v100, fine, tool3; ! 6. ???? ???? ?? ??? ?????.
        RestoPath;             ! 7. ???? ??? ?????.
        StartMove;             ! 8. ????? ??? ??? ??????.
    ENDTRAP

ENDMODULE